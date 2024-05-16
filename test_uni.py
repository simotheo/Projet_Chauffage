import unittest
from genereJSon import genereJSon
from datetime import datetime, timedelta, timezone
from create_file_icalendar import create_icalendar_file
from verif_lien_ade import liens_reussi
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from recuperation import heure_debut, heure_fin, supprime_fichier, recuperation, make_chemin
from recup_mqtt import connexion_mqtt, subscribe_mqtt, deconnexion_mqtt
from envoie_mqtt import envoie_mqtt
from unittest.mock import MagicMock
from connexion import connexion, writeData, readData, affiche_res, close
from paho.mqtt.client import Client as MQTTClient
import pytz

class TestGenereJSon(unittest.TestCase):
    """Test le module genereJSon.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    def test_base10_integer(self):
        """Teste la génération de JSON avec un entier en base 10.
        """
        temp_en_base_10 = 20
        json_result = genereJSon(temp_en_base_10)
        self.assertIsNotNone(json_result)
        self.assertTrue(isinstance(json_result, str))

    def test_non_base10_input(self):
        """Teste la génération de JSON avec une entrée non base 10.
        """
        temp_non_base_10 = 'abc'
        json_result = genereJSon(temp_non_base_10)
        self.assertIsNone(json_result)

    def test_invalid_character(self):
        """Teste la génération de JSON avec un caractère invalide.
        """
        temp_invalid_character = 20.5
        json_result = genereJSon(temp_invalid_character)
        self.assertIsNone(json_result)

class TestCreateICalendar(unittest.TestCase):
    """Teste le module create_file_icalendar.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    def test_correct_information(self):
        """Teste la création d'un fichier iCalendar avec des informations correctes.
        """
        salle = '8C-030 CHR*  (32pl./32 écrans sans PC)VP TB'
        horaires = [(datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)), (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)), (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0))]
        summaries = ['Occupation Salle 1', 'Reunion', 'Maintenance']
        create_icalendar_file(salle, horaires, summaries)
        expected_filename = 'calendrier_8C-030_CHR__(32pl.32_écrans_sans_PC)VP_TB.ics'
        self.assertTrue(os.path.exists(expected_filename), f"File '{expected_filename}' does not exist.")

    def test_invalid_hours(self):
        """Teste la création d'un fichier iCalendar avec des horaires invalides.
        """
        salle = '8C-030 CHR*  (32pl./32 écrans sans PC)VP TB'
        horaires = [(datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)), (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)), (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0))]
        summaries = ['Occupation Salle 1', 'Reunion', 'Maintenance']
        create_icalendar_file(salle, horaires, summaries)
        expected_filename = 'calendrier_8C-030_CHR__(32pl.32_écrans_sans_PC)VP_TB.ics'
        self.assertTrue(os.path.exists(expected_filename), f"File '{expected_filename}' does not exist.")

    def test_invalid_input(self):
        """Teste la création d'un fichier iCalendar avec des entrées invalides.
        """
        salle = '8C-030 CHR*  (32pl./32 écrans sans PC)VP TB'
        horaires = ['invalid']
        summaries = ['Invalid']
        with self.assertRaises(ValueError):
            create_icalendar_file(salle, horaires, summaries)

class TestLiensReussi(unittest.TestCase):
    """Teste le module verif_lien_ade.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    @patch('verif_lien_ade.requests.get')
    def test_liens_reussi_succes(self, mock_get):
        """Teste la fonction liens_reussi avec un succès de la requête.

        Args:
            mock_get (MagicMock): Mock de la fonction requests.get
        """
        mock_get.return_value.status_code = 200
        resultat = liens_reussi()
        self.assertEqual(resultat, 'True')

    @patch('verif_lien_ade.requests.get')
    def test_liens_reussi_echec(self, mock_get):
        """Teste la fonction liens_reussi avec un échec de la requête.

        Args:
            mock_get (MagicMock): Mock de la fonction requests.get
        """
        mock_get.return_value.status_code = 404
        resultat = liens_reussi()
        self.assertEqual(resultat, 'False')

    def test_format_date(self):
        """Teste la fonction format_date.
        """
        resultat = liens_reussi()
        self.assertIn('True', resultat)

class TestRecuperation(unittest.TestCase):
    """Teste le module recuperation.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    def setUp(self):
        """Initialise les données de test.
        """
        self.ics_content = b'BEGIN:VCALENDAR\nBEGIN:VEVENT\nDTSTART:20240101T120000Z\nDTEND:20240101T130000Z\nEND:VEVENT\nEND:VCALENDAR\n'
        self.test_ics_file = 'test.ics'
        with open(self.test_ics_file, 'wb') as f:
            f.write(self.ics_content)

    def tearDown(self):
        """Nettoie les données de test.
        """
        Path(self.test_ics_file).unlink()

    def test_heure_debut(self):
        """Teste la fonction heure_debut.
        """
        paris_tz = pytz.timezone('Europe/Paris')
        expected_time = paris_tz.localize(datetime(2024, 1, 1, 13, 0))
        result_time = heure_debut(self.test_ics_file)
        self.assertEqual(paris_tz.normalize(result_time), paris_tz.normalize(expected_time))

    def test_heure_fin(self):
        """Teste la fonction heure_fin.
        """
        paris_tz = pytz.timezone('Europe/Paris')
        expected_time = paris_tz.localize(datetime(2024, 1, 1, 14, 0))
        result_time = heure_fin(self.test_ics_file)
        self.assertEqual(paris_tz.normalize(result_time), paris_tz.normalize(expected_time))

    def test_supprime_fichier(self):
        """Teste la fonction supprime_fichier.
        """
        test_file = 'test_file.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        self.assertTrue(supprime_fichier(test_file))
        self.assertFalse(Path(test_file).exists())

    @patch('recuperation.requests.get')
    def test_recuperation(self, mock_get):
        """Teste la fonction recuperation.

        Args:
            mock_get (MagicMock): Mock de la fonction requests.get
        """
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = self.ics_content
        self.assertTrue(recuperation('https://exemple.com/fichier.ics', 'test_file.ics'))
        self.assertTrue(Path('test_file.ics').exists())

    def test_make_chemin(self):
        """Teste la fonction make_chemin.
        """
        with patch('recuperation.nom_salle', return_value='fichier'):
            self.assertEqual(make_chemin('https://exemple.com/fichier.ics'), 'fichier.ics')

class TestRecupMQTT(unittest.TestCase):
    """Teste les modules recup_mqtt et envoie_mqtt.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    @patch('recup_mqtt.mqtt.Client')
    def test_connexion_mqtt_success(self, MockClient):
        """Teste la fonction connexion_mqtt avec succès.

        Args:
            MockClient (MagicMock): Mock de la classe mqtt.Client
        """
        mock_client = MockClient.return_value
        mock_client.connected_flag = False
        broker = 'test_broker'
        username = 'test_user'
        password = 'test_password'
        with patch('recup_mqtt.broker', broker), patch('recup_mqtt.username', username), patch('recup_mqtt.password', password), patch('recup_mqtt.time.sleep', return_value=None):

            def mock_connect(broker):
                """Mock de la fonction connect.

                Args:
                    broker (str): Adresse du broker
                """
                mock_client.connected_flag = True
            mock_client.connect.side_effect = mock_connect
            result = connexion_mqtt('test/topic')
            mock_client.connect.assert_called_with(broker)
            mock_client.username_pw_set.assert_called_with(username, password)
            self.assertTrue(mock_client.connected_flag)
            self.assertEqual(result, mock_client)

    @patch('recup_mqtt.mqtt.Client')
    def test_subscribe_mqtt_success(self, MockClient):
        """Teste la fonction subscribe_mqtt avec succès.

        Args:
            MockClient (MagicMock): Mock de la classe mqtt.Client
        """
        mock_client = MockClient.return_value
        mock_client.subscribe.return_value = (0, 1)
        result = subscribe_mqtt(mock_client, 'topic_down', 'topic_up')
        mock_client.subscribe.assert_any_call('topic_up')
        mock_client.subscribe.assert_any_call('topic_down')
        self.assertTrue(result)

    @patch('recup_mqtt.mqtt.Client')
    def test_deconnexion_mqtt_success(self, MockClient):
        """Teste la fonction deconnexion_mqtt avec succès.

        Args:
            MockClient (MagicMock): Mock de la classe mqtt.Client
        """
        mock_client_instance = MockClient.return_value
        deconnexion_mqtt(mock_client_instance)
        mock_client_instance.disconnect.assert_called_once()

class TestEnvoieMQTT(unittest.TestCase):
    """Teste le module envoie_mqtt.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    def test_envoie_mqtt_success(self):
        """Teste la fonction envoie_mqtt avec succès.
        """
        client = MagicMock()
        client.publish.return_value = (0, 0)
        result = envoie_mqtt(client, 'topic', 'payload')
        self.assertTrue(result)

    def test_envoie_mqtt_failure(self):
        """Teste la fonction envoie_mqtt avec échec.
        """
        client = MagicMock()
        client.publish.return_value = (1, 2)
        result = envoie_mqtt(client, 'topic', 'payload')
        self.assertFalse(result)

class TestConnexionInfluxDB(unittest.TestCase):
    """Teste le module connexion.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire
    """

    @patch('connexion.influxdb_client.InfluxDBClient')
    def test_connexion_influxdb_success(self, MockInfluxDBClient):
        """Teste la fonction connexion.

        Args:
            MockInfluxDBClient (MagicMock): Mock de la classe InfluxDBClient
        """
        client = MockInfluxDBClient.return_value
        result = connexion('http://test_host', 'test_token', 'test_org')
        self.assertEqual(result, client)

    @patch('connexion.influxdb_client.InfluxDBClient')
    def test_write_data_success(self, MockInfluxDBClient):
        """Teste la fonction writeData.

        Args:
            MockInfluxDBClient (MagicMock): Mock de la classe InfluxDBClient
        """
        client = MockInfluxDBClient.return_value
        write_api = client.write_api.return_value
        write_api.write.return_value = None
        heure = datetime.utcnow()
        writeData(client, 'test_bucket', 'test_org', 'salle_test', 25.0, heure, heure)
        write_api.write.assert_called_once()

    @patch('connexion.influxdb_client.InfluxDBClient')
    def test_read_data_success(self, MockInfluxDBClient):
        """Teste la fonction readData.

        Args:
            MockInfluxDBClient (MagicMock): Mock de la classe InfluxDBClient
        """
        client = MockInfluxDBClient.return_value
        query_api = client.query_api.return_value
        query_api.query.return_value = [{'field': 'value'}]
        result = readData(client, 'test_org', 'salle_test')
        self.assertEqual(result, [{'field': 'value'}])

    def test_affiche_res(self):
        """Teste la fonction affiche_res.
        """
        mock_result = [MagicMock(records=[MagicMock(get_field=MagicMock(return_value='field1'), get_value=MagicMock(return_value='value1')), MagicMock(get_field=MagicMock(return_value='field2'), get_value=MagicMock(return_value='value2'))])]
        import sys
        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output
        affiche_res(mock_result)
        sys.stdout = sys.__stdout__
        expected_output = "[('field1', 'value1'), ('field2', 'value2')]"
        self.assertEqual(captured_output.getvalue().strip(), expected_output)

    def test_close_connexion(self):
        """Teste la fonction close.
        """
        client = MagicMock()
        close(client)
        client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
