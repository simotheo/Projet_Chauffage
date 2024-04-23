import unittest
from genereJSon import genereJSon
from datetime import datetime, timedelta
from create_file_icalendar import create_icalendar_file
import os

#
class TestGenereJSon(unittest.TestCase):
    def test_base10_integer(self):
        temp_en_base_10 = 20
        json_result = genereJSon(temp_en_base_10)
        self.assertIsNotNone(json_result)
        self.assertTrue(isinstance(json_result, str))
        
    def test_non_base10_input(self):
        temp_non_base_10 = 'abc'
        json_result = genereJSon(temp_non_base_10)
        self.assertIsNone(json_result)
        
    def test_invalid_character(self):
        temp_invalid_character = 20.5
        json_result = genereJSon(temp_invalid_character)
        self.assertIsNone(json_result)



class TestCreateICalendar(unittest.TestCase):
    def test_correct_information(self):
        salle = "8C-030 CHR*  (32pl./32 écrans sans PC)VP TB"
        horaires = [
            (datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)),
            (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)),
            (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0)),
        ]
        summaries = ["Occupation Salle 1", "Reunion", "Maintenance"]

        create_icalendar_file(salle, horaires, summaries)

        # Nom de fichier attendu
        expected_filename = "calendrier_8C-030_CHR__(32pl.32_écrans_sans_PC)VP_TB.ics"

        # Vérifiez si le fichier a été créé avec le bon nom
        self.assertTrue(os.path.exists(expected_filename), f"File '{expected_filename}' does not exist.")

    def test_invalid_hours(self):
        salle = "8C-030 CHR*  (32pl./32 écrans sans PC)VP TB"
        horaires = [
            (datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)),
            (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)),
            (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0)),
        ]
        summaries = ["Occupation Salle 1", "Reunion", "Maintenance"]

        create_icalendar_file(salle, horaires, summaries)

        # Nom de fichier attendu
        expected_filename = "calendrier_8C-030_CHR__(32pl.32_écrans_sans_PC)VP_TB.ics"

        # Vérifiez si le fichier a été créé avec le bon nom
        self.assertTrue(os.path.exists(expected_filename), f"File '{expected_filename}' does not exist.")



    def test_invalid_input(self):
        salle = "8C-030 CHR*  (32pl./32 écrans sans PC)VP TB"
        # Horaires invalides : passer une chaîne de caractères au lieu d'une liste d'horaires
        horaires = ["invalid"]
        summaries = ["Invalid"]

        # On s'attend à ce que cette fonction lève une exception ValueError
        with self.assertRaises(ValueError):
            create_icalendar_file(salle, horaires, summaries)



if __name__ == '__main__':
    unittest.main()
