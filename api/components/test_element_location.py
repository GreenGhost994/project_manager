import unittest
from api.components.element_location import *


class Test_ElementLocation(unittest.TestCase):
    
    data_building = {"buildings":
                            {
                                "HUS1":
                                    {"grid_lines":
                                        {
                                            "1": [[0, 0], [0, 50000]],
                                            "2": [[6000, 0], [6000, 50000]],
                                            "3": [[12000, 0], [12000, 50000]],
                                            "4": [[18000, 0], [18000, 50000]],
                                            "5": [[24000, 0], [24000, 50000]],
                                            "6": [[40000, 0], [40000, 50000]],
                                            "7": [[40005, 0], [40005, 50000]],
                                            "A": [[0, 0], [30000, 0]],
                                            "B": [[0, 6000], [50000, 6000]],
                                            "C": [[0, 12000], [50000, 12000]],
                                            "D": [[0, 18000], [50000, 18000]],
                                            "E": [[0, 20000], [50000, 20000]],
                                            "F": [[0, 30000], [50000, 30000]]
                                        }
                                    },
                                "HUS2":
                                    {"grid_lines":
                                        {
                                            "1": [[0, 0], [0, -50000]],
                                            "2": [[-6000, 0], [-6000, -50000]],
                                            "3": [[-12000, 0], [-12000, -50000]],
                                            "4": [[-18000, 0], [-18000, -50000]],
                                            "5": [[-24000, 0], [-24000, -50000]],
                                            "6": [[-40000, 0], [-40000, -50000]],
                                            "A": [[0, 0], [-30000, 0]],
                                            "B": [[0, -6000], [-30000, -6000]],
                                            "C": [[0, -12000], [-30000, -12000]],
                                            "D": [[0, -18000], [-30000, -18000]],
                                            "E": [[0, -20000], [-30000, -20000]],
                                            "F": [[0, -30000], [-30000, -30000]]
                                        }
                                    }
                            }
                        }
    
    def test_procedure_element1(self):
        data_elemnet = {"elements":
            [
                {"element_name": "C_01", "coords": [6000, 5900, 1500], "rotation": [0], "size": [600, 600, 3000]},
                {"element_name": "C_02", "coords": [11700, 5700, 1500], "rotation": [45], "size": [600, 600, 3000]},
                {"element_name": "C_03", "coords": [18000, 12100, 1500], "rotation": [0], "size": [600, 600, 3000]},
            ]
        }
       
        processed_data = process_data(self.data_building | data_elemnet)
        expected_data = [['C_01', 'HUS1', '2/B'], ['C_02', 'HUS1', '3/B'], ['C_03', 'HUS1', '4/C']]
        self.assertCountEqual([[x[0][0], x[1], x[2][0]] for x in processed_data], expected_data)    
        

    def test_procedure_element2(self):
        data_elemnet = {"elements":
            [
                {"element_name": "W_01", "coords": [6000, 5900, 1500], "rotation": [0], "size": [4300, 200, 2000]},
                {"element_name": "W_02", "coords": [6000, 9900, 1500], "rotation": [0], "size": [4300, 200, 2000]},
                {"element_name": "W_03", "coords": [6000, 5900, 1500], "rotation": [0], "size": [4300, 200, 2000]},
            ]
        }
       
        processed_data = process_data(self.data_building | data_elemnet)
        expected_data = [['W_01', 'HUS1', '2-3/B'], ['W_03', 'HUS1', '2-3/B'], ['W_02', 'HUS1', '2-3/B-C']]
        self.assertCountEqual([[x[0][0], x[1], x[2][0]] for x in processed_data], expected_data)
        

    def test_procedure_element3(self):
        data_elemnet = {"elements":
            [
                {"element_name": "WS_01", "coords": [9000, 5900, 1500], "rotation": [0], "size": [4300, 200, 2000]},
                {"element_name": "WS_02", "coords": [9000, 11900, 1500], "rotation": [0], "size": [4300, 200, 2000]},
                {"element_name": "WS_03", "coords": [6000, 11900, 1500], "rotation": [0], "size": [4300, 200, 2000]},
            ]
        }
       
        processed_data = process_data(self.data_building | data_elemnet)
        expected_data = [['WS_01', 'HUS1', '2-4/B'], ['WS_02', 'HUS1', '2-4/C'], ['WS_03', 'HUS1', '2-3/C']]
        self.assertCountEqual([[x[0][0], x[1], x[2][0]] for x in processed_data], expected_data)
        

    def test_procedure_element_boundary1(self):
        data_elemnet = {"elements":
            [
                {"element_name": "WS_01", "coords": [9000, 5900, 1500], "rotation": [0], "boundary": [[9000, 5600, 1500], [19000, 5600, 1500], [19000, 5900, 1500], [9000, 5900, 1500]]},
            ]
        }

        processed_data = process_data(self.data_building | data_elemnet)
        expected_data = [['WS_01', 'HUS1', '2-5/B']]
        self.assertCountEqual([[x[0][0], x[1], x[2][0]] for x in processed_data], expected_data)
        

    def test_procedure_element_close_axis1(self):
        data_elemnet = {"elements":
            [
                {"element_name": "W_001", "coords": [39900, 5900, 1500], "rotation": [-90], "boundary": [[39905, 5900, 1500], [41005, 5900, 1500], [41005, 8900, 1500], [39905, 8900, 1500]]},
            ]
        }

        processed_data = process_data(self.data_building | data_elemnet)
        expected_data = [['W_001', 'HUS1', '7/B-C']]

        self.assertCountEqual([[x[0][0], x[1], x[2][0]] for x in processed_data], expected_data)

