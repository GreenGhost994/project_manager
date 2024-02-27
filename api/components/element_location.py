from shapely import affinity, LineString, Point, Polygon
from functools import wraps
import time

def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper

AREA_SIZE = {'mm': 1000, 'm': 1}
MAX_SIZE = 2*15


def process_data(data: dict):
    elements = elements_geometry(data['elements'])
    elements_with_location = []
    for b_name, b_data in data['buildings'].items():
        unit = unit_recognition(data)
        axis_intersections = intersection_recognition(b_data)

        # point analyze
        elements_found, elements = zone_analyze(elements, axis_intersections, unit, b_name, quad_segs=3)
        if elements_found:
            elements_with_location += elements_found
        if not elements:
            return elements_with_location
        
        line_zones, area_zones = line_area_recognition(axis_intersections, unit)
                   
        # line analyze
        elements_found, elements = zone_analyze(elements, line_zones, unit, b_name)
        if elements_found:
            elements_with_location += elements_found
        if not elements:
            return elements_with_location               
                       
        # area analyze
        elements_found, elements = zone_analyze(elements, area_zones, unit, b_name)
        if elements_found:
            elements_with_location += elements_found
        if not elements:
            return elements_with_location

        return elements_with_location + [[x, 'Not found', ('Not found', None)] for x in elements]

def elements_geometry(elements: dict) -> dict:
    """
    Convert input data to dict of element geometry.
    """
    elements_data = []

    for element_data in elements:
        if 'size' in element_data:
            p1 = Point(element_data['coords'])
            p2 = affinity.affine_transform(p1, [1, 0, 0, 0, 1, 0, 0, 0, 1, element_data['size'][0], 0, 0])
            p3 = affinity.affine_transform(p1, [1, 0, 0, 0, 1, 0, 0, 0, 1, element_data['size'][0], element_data['size'][1], 0])
            p4 = affinity.affine_transform(p1, [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, element_data['size'][1], 0])
            geometry = affinity.rotate(Polygon([p1, p2, p3, p4]), element_data['rotation'][0], origin=p1)
            elements_data.append([element_data["element_name"], geometry])
        elif 'boundary' in element_data:
            elements_data.append([element_data["element_name"], Polygon(element_data["boundary"])])

    return elements_data


def unit_recognition(data: dict) -> str:
    """
    Check units of model based on grid boundary.
    """
    max_x, max_y, min_x, min_y = float('-inf'),  float('-inf'), float('inf'), float('inf')

    for b_data in data['buildings'].values():
        for g_data in b_data.values():
            for axis in g_data.values():
                for vertex in axis:
                    x, y = vertex

                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)

    diff_x = max_x - min_x
    diff_y = max_y - min_y

    if 3000 < diff_x < 3000000 and 3000 < diff_y < 3000000:
        return "mm"
    elif 0 < diff_x < 3000 and 0 < diff_y < 3000:
        return "m"

    return "Undefined"


def intersection_recognition(b_data: dict) -> list:
    """
    Identify all axis intersections.
    """
    intersections = []
    processed_combinations = set()

    grid_lines = b_data['grid_lines']

    for axis1_name, axis1_data in grid_lines.items():
        for axis2_name, axis2_data in grid_lines.items():
            if axis1_name != axis2_name:
                    
                combination1 = (axis1_name, axis2_name)
                combination2 = (axis2_name, axis1_name)
                if combination1 in processed_combinations or combination2 in processed_combinations:
                    continue

                line1 = LineString(axis1_data)
                line2 = LineString(axis2_data)
                intersection = line1.intersection(line2)

                if intersection.is_empty:
                    continue

                if intersection.geom_type == 'Point':
                    intersections.append(((axis1_name, axis2_name), intersection))
                    processed_combinations.add(combination1)

    return intersections


def line_area_recognition(intersections: list, unit: str):
    """
    Identify all axis and area zones.
    """

    def has_common(i1, i2):
        merged = i1 + i2
        mergedset = set(merged)
        if len(merged) != len(mergedset):
            return True
        return False

    def find_third_point(name1, name2):
        for i in intersections:
            if (i[0][0] == name1 and i[0][1] == name2) or (i[0][0] == name2 and i[0][1] == name1):
                return i
        return False
    
    line_zones = []
    area_zones = []

    for id_i1, i1 in enumerate(intersections):
        for i2 in intersections[id_i1+1:]:
            if has_common(i1[0], i2[0]):
                line = LineString((i1[1], i2[1]))
                if line.length < MAX_SIZE * AREA_SIZE[unit]:
                    line_zones.append((
                        f"{'-'.join(sorted(set((i1[0][0], i2[0][0]))))}/{'-'.join(sorted(set((i1[0][1], i2[0][1]))))}",
                        line
                        ))
            else:
                p2 = find_third_point(i1[0][0], i2[0][1])
                p4 = find_third_point(i1[0][1], i2[0][0])
                if p2 and p4:
                    polygon = Polygon((i1[1], p2[1], i2[1], p4[1]))
                    if polygon.area < (MAX_SIZE * AREA_SIZE[unit])**2:
                        area_zones.append((
                            f"{'-'.join(sorted((i1[0][0], i2[0][0])))}/{'-'.join(sorted((i1[0][1], i2[0][1])))}",
                            polygon
                            ))
    return line_zones, area_zones


def zone_analyze(elements: list, zones: list, unit: str, building="", quad_segs=1):
    elements_found = []
    buffer_zones = []
    for i in zones:
        zone_name = i[0]
        if isinstance(i[0], tuple):
            zone_name = '/'.join(i[0])
        area_shape = i[1].buffer(AREA_SIZE[unit], quad_segs)
        buffer_zones.append((zone_name, area_shape, area_shape.area)) 

    buffer_zones.sort(key=lambda x: x[2])

    for ele in elements:
        ele_location = []
        ele_cog = ele[1].centroid
        found_location = False
        smallest_area = -1
        ele1area = ele[1].area

        for i in buffer_zones:
            if found_location and smallest_area != i[1].area:
                break

            if i[1].contains(ele_cog):
                if ele1area * 0.99 <= ele[1].intersection(i[1]).area <= ele1area * 1.01:
                    found_location = True
                    smallest_area = i[1].area
                    ele_location.append(i)


        if ele_location:
            target_loc = ele_location[0]
            target_area = ele_location[0][1].area
            target_distance = (ele_location[0][1].centroid).distance(ele_cog)
            for loc in ele_location:
                loc_area = loc[1].area
                loc_centroid = loc[1].centroid
                if loc_area < target_area:
                    target_loc = loc
                    target_area = loc_area
                    target_distance = (loc_centroid).distance(ele_cog)
                elif loc_area == target_area:
                    if (loc_centroid).distance(ele_cog) < target_distance:
                        target_loc = loc
                        target_area = loc_area
                        target_distance = (loc_centroid).distance(ele_cog)

            elements_found.append((ele, building, target_loc))

    for i in elements_found:
        elements.remove(i[0])

    return elements_found, elements
