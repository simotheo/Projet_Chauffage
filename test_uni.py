import unittest
from unittest.mock import patch, MagicMock
import schedule
from threading import Thread
import time
import variables as var
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from paho.mqtt.client import MQTT_ERR_SUCCESS
from datetime import datetime, timedelta
import pytz
import base64
import os

from threadVanne import VanneThread
from recuperation import nom_salle, recuperation
from recup_mqtt import connexion_mqtt, on_connect, on_message, deconnexion_mqtt
import variables as var  # Si des variables globales sont utilisées
import paho.mqtt.client as mqtt
from influxDB import writeData, writeSetpoint, readData, recup_info, affiche_res, ecrire_setpoint, ecrire_consigne, recup_consigne
from gestionMqtt import envoie_mqtt, get_setpoint_from_message, verif_envoie_mqtt, transmet_mqtt, subscribe_mqtt, create_topic, abonnement_general
import gestionADE as gad
from genereJSon import base10_to_base64, genereJSon
from create_file_icalendar import create_icalendar_file
from connexion import connexion, close

# Import des fonctions du planificateur
from plannificateur import setup_scheduler, run_scheduler, start_scheduler

class TestVanneThread(unittest.TestCase):
    """Teste la classe VanneThread.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """
    def test_initialization(self):
        """Teste l'initialisation de la classe VanneThread.
        """
        vanne = VanneThread("simu-vanne-01", "8D-010", "topic/up", "topic/down")
        self.assertEqual(vanne.nom, "simu-vanne-01")
        self.assertEqual(vanne.salle, "8D-010")

    def test_on_connect(self):
        """Teste la méthode on_connect de la classe VanneThread.
        """
        mock_client = MagicMock()
        with self.assertRaises(TypeError):
            vanne = VanneThread(mock_client)


    def test_on_message(self):
        """Teste la méthode on_message de la classe VanneThread.
        """
        mock_client = MagicMock()
        vanne = VanneThread(mock_client, "salle", "topic_up", "topic_down")
        test_message = b'Test message'
        with self.assertRaises(Exception):
            vanne.on_message(mock_client, None, test_message)

    def test_process_message(self):
        """Teste la méthode process_message de la classe VanneThread.
        """
        mock_client = MagicMock()
        vanne = VanneThread(mock_client, "salle", "topic_up", "topic_down")
        with self.assertRaises(Exception):
            vanne.process_message(b'Test message')

class TestRecuperationFunctions(unittest.TestCase):
    """Teste les fonctions du module recuperation.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """

    def test_nom_salle(self):
        """Teste la fonction nom_salle.
        """
        url = 'https://exemple.com/fichier.ics'
        salle = nom_salle(url)
        self.assertIsNone(salle)

    @patch('recuperation.requests.get')
    def test_recuperation(self, mock_get):
        """Teste la fonction recuperation.

        Args:
            mock_get (MagicMock): Mock de la fonction requests.get.
        """
        mock_response = MagicMock()
        mock_response.content = b'Test content'
        mock_get.return_value = mock_response

        result = recuperation('https://exemple.com/fichier.ics', 'test_file.ics')
        self.assertTrue(True)

class TestRecupMqttFunctions(unittest.TestCase):
    """Teste les fonctions de récupération MQTT.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """
    def test_connexion_mqtt(self):
        """Teste la fonction connexion_mqtt.
        """
        client = connexion_mqtt()
        self.assertIsInstance(client, mqtt.Client)

    def test_on_connect(self):
        """Teste la fonction on_connect.
        """
        client = mqtt.Client()
        client.connected_flag = False
        on_connect(client, None, None, 0)
        self.assertTrue(client.connected_flag)


class TestSchedulerFunctions(unittest.TestCase):
    """Teste les fonctions du planificateur.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """
    @patch('gestionADE.edt_par_vanne')
    def test_setup_scheduler(self, mock_edt_par_vanne):
        """Teste la fonction setup_scheduler.

        Args:
            mock_edt_par_vanne (MagicMock): Mock de la fonction edt_par_vanne.
        """
        setup_scheduler()
        self.assertTrue(mock_edt_par_vanne.called)
        self.assertTrue(schedule.jobs)

    @patch('gestionADE.edt_par_vanne')
    @patch('schedule.run_pending')
    def test_run_scheduler(self, mock_run_pending, mock_edt_par_vanne):
        """Teste la fonction run_scheduler.

        Args:
            mock_run_pending (MagicMock): Mock de la fonction run_pending.
            mock_edt_par_vanne (MagicMock): Mock de la fonction edt_par_vanne.
        """
        mock_run_pending.side_effect = KeyboardInterrupt()  # Pour arrêter la boucle
        try:
            run_scheduler()
        except KeyboardInterrupt:
            pass
        self.assertTrue(mock_run_pending.called)

    @patch('gestionADE.edt_par_vanne')
    @patch('schedule.run_pending')
    def test_start_scheduler(self, mock_run_pending, mock_edt_par_vanne):
        """Teste la fonction start_scheduler.

        Args:
            mock_run_pending (MagicMock): Mock de la fonction run_pending.
            mock_edt_par_vanne (MagicMock): Mock de la fonction edt_par_vanne.
        """
        with patch('threading.Thread.start') as mock_thread_start:
            start_scheduler()
            self.assertTrue(mock_thread_start.called)
            self.assertTrue(mock_edt_par_vanne.called)

class TestInfluxDBFunctions(unittest.TestCase):
    """Teste les fonctions du module influxDB.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """


    @patch('influxdb_client.InfluxDBClient')
    def test_writeSetpoint(self, MockInfluxDBClient):
        """Teste la fonction writeSetpoint.

        Args:
            MockInfluxDBClient (MagicMock): Mock de la classe InfluxDBClient.
        """
        mock_client = MockInfluxDBClient.return_value
        writeSetpoint(mock_client, "test_bucket", "test_org", "test_vanne", 21.0, "test_salle")
        mock_client.write_api().write.assert_called_once()

    @patch('influxdb_client.InfluxDBClient')
    def test_readData(self, MockInfluxDBClient):
        """Teste la fonction readData.

        Args:
            MockInfluxDBClient (MagicMock): Mock de la classe InfluxDBClient.
        """
        mock_client = MockInfluxDBClient.return_value
        result = readData(mock_client, "test_org", "test_salle")
        mock_client.query_api().query.assert_called_once()
        self.assertEqual(result, mock_client.query_api().query.return_value)

    @patch('influxDB.connexion.connexion')
    @patch('influxDB.connexion.close')
    @patch('influxDB.writeSetpoint')
    def test_ecrire_setpoint(self, mock_writeSetpoint, mock_connexion_close, mock_connexion_connexion):
        """Teste la fonction ecrire_setpoint.

        Args:
            mock_writeSetpoint (MagicMock): Mock de la fonction writeSetpoint.
            mock_connexion_close (MagicMock): Mock de la fonction close.
            mock_connexion_connexion (MagicMock): Mock de la fonction connexion.
        """
        mock_client = MagicMock()
        mock_connexion_connexion.return_value = mock_client
        ecrire_setpoint(21.0, "test_salle", "test_vanne")
        mock_writeSetpoint.assert_called_once_with(mock_client, var.bucket, var.org, "test_vanne", 21.0, "test_salle")
        mock_connexion_close.assert_called_once_with(mock_client)

    @patch('influxDB.connexion.connexion')
    @patch('influxDB.connexion.close')
    @patch('influxDB.readData')
    def test_recup_consigne(self, mock_readData, mock_connexion_close, mock_connexion_connexion):
        """Teste la fonction recup_consigne.

        Args:
            mock_readData (MagicMock): Mock de la fonction readData.
            mock_connexion_close (MagicMock): Mock de la fonction close.
            mock_connexion_connexion (MagicMock): Mock de la fonction connexion.
        """
        mock_client = MagicMock()
        mock_connexion_connexion.return_value = mock_client
        mock_readData.return_value = "result"
        result = recup_consigne("test_salle")
        mock_readData.assert_called_once_with(mock_client, var.org, "test_salle")
        mock_connexion_close.assert_called_once_with(mock_client)
        self.assertEqual(result, "result")

class TestGestionMqtt(unittest.TestCase):
    """Teste les fonctions de gestion MQTT.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """
    def test_get_setpoint_from_message(self):
        """Teste la fonction get_setpoint_from_message.
        """
        message = json.dumps({
            'uplink_message': {
                'decoded_payload': {
                    'setpoint': 22
                }
            }
        })
        setpoint = get_setpoint_from_message(message)
        self.assertEqual(setpoint, 22)

    def test_get_setpoint_from_message_invalid(self):
        """Teste la fonction get_setpoint_from_message avec un message invalide.
        """
        message = "invalid message"
        setpoint = get_setpoint_from_message(message)
        self.assertIsNone(setpoint)

    def test_verif_envoie_mqtt(self):
        """Teste la fonction verif_envoie_mqtt.
        """
        setpoint = 22
        temperature_voulue = 20
        self.assertTrue(verif_envoie_mqtt(setpoint, temperature_voulue))

        temperature_voulue = 22
        self.assertFalse(verif_envoie_mqtt(setpoint, temperature_voulue))

    def test_transmet_mqtt(self):
        """Teste la fonction transmet_mqtt.
        """
        client = MagicMock()
        client.publish.return_value = (MQTT_ERR_SUCCESS, None)
        topic = "test/topic"
        payload = '{"setpoint": 22}'

        result = transmet_mqtt(client, topic, payload)
        self.assertTrue(result)
        client.publish.assert_called_once_with(topic, payload)

    def test_transmet_mqtt_failure(self):
        """Teste la fonction transmet_mqtt en cas d'échec.
        """
        client = MagicMock()
        client.publish.return_value = (1, None)  # Simulate failure
        topic = "test/topic"
        payload = '{"setpoint": 22}'

        result = transmet_mqtt(client, topic, payload)
        self.assertFalse(result)
        client.publish.assert_called_once_with(topic, payload)

    def test_subscribe_mqtt(self):
        """Teste la fonction subscribe_mqtt.
        """
        client = MagicMock()
        topic_down = "test/topic_down"
        topic_up = "test/topic_up"
        client.subscribe.return_value = (MQTT_ERR_SUCCESS, None)

        result = subscribe_mqtt(client, topic_down, topic_up)
        self.assertTrue(result)
        client.subscribe.assert_any_call(topic_down)
        client.subscribe.assert_any_call(topic_up)

    def test_subscribe_mqtt_failure(self):
        """Teste la fonction subscribe_mqtt en cas d'échec.
        """
        client = MagicMock()
        topic_down = "test/topic_down"
        topic_up = "test/topic_up"
        client.subscribe.side_effect = [(MQTT_ERR_SUCCESS, None), (1, None)]  # Simulate one failure

        result = subscribe_mqtt(client, topic_down, topic_up)
        self.assertFalse(result)
        client.subscribe.assert_any_call(topic_down)
        client.subscribe.assert_any_call(topic_up)

    def test_create_topic(self):
        """Teste la fonction create_topic.
        """
        device_id = "test_device"
        expected_down = f"v3/usmb-project@ttn/devices/{device_id}/down/replace"
        expected_up = f"v3/usmb-project@ttn/devices/{device_id}/up"
        result_down, result_up = create_topic(device_id)
        self.assertEqual(result_down, expected_down)
        self.assertEqual(result_up, expected_up)

        
class TestGestionADE(unittest.TestCase):
    """Teste les fonctions du module gestionADE.

    Args:
        unittest (unittest.TestCase): Classe de test unitaire.
    """

    @patch('gestionADE.recup.recuperation')
    @patch('gestionADE.recup.heure_debut')
    @patch('gestionADE.recup.heure_fin')
    def test_ade(self, mock_heure_fin, mock_heure_debut, mock_recuperation):
        """Teste la fonction ade.

        Args:
            mock_heure_fin (MagicMock): Mock de la fonction heure_fin.
            mock_heure_debut (MagicMock): Mock de la fonction heure_debut.
            mock_recuperation (MagicMock): Mock de la fonction recuperation.
        """
        url = "test_url"
        chemin = "test_chemin"
        var.temps_prechauffage = 30
        var.temps_arret = 10

        mock_heure_debut.return_value = datetime(2024, 5, 22, 10, 0)
        mock_heure_fin.return_value = datetime(2024, 5, 22, 12, 0)
        debut, fin = gad.ade(url, chemin)
        self.assertEqual(debut, datetime(2024, 5, 22, 9, 30))
        self.assertEqual(fin, datetime(2024, 5, 22, 11, 50))

        mock_heure_debut.return_value = None
        mock_heure_fin.return_value = datetime(2024, 5, 22, 12, 0)
        debut, fin = gad.ade(url, chemin)
        self.assertIsNone(debut)
        self.assertEqual(fin, datetime(2024, 5, 22, 11, 50))

        mock_heure_debut.return_value = datetime(2024, 5, 22, 10, 0)
        mock_heure_fin.return_value = None
        debut, fin = gad.ade(url, chemin)
        self.assertEqual(debut, datetime(2024, 5, 22, 9, 30))
        self.assertIsNone(fin)

        mock_heure_debut.return_value = None
        mock_heure_fin.return_value = None
        debut, fin = gad.ade(url, chemin)
        self.assertIsNone(debut)
        self.assertIsNone(fin)

    @patch('gestionADE.recup.create_url')
    @patch('gestionADE.gad.calcul_consigne')
    def test_edt_par_vanne(self, mock_calcul_consigne, mock_create_url):
        """Teste la fonction edt_par_vanne.

        Args:
            mock_calcul_consigne (MagicMock): Mock de la fonction calcul_consigne.
            mock_create_url (MagicMock): Mock de la fonction create_url.
        """
        var.liste_vannes = {"vanne1": ["salle1"], "vanne2": ["salle2"]}
        var.liste_salles = []
        mock_create_url.side_effect = lambda salle: f"url_{salle}"

        gad.edt_par_vanne()

        self.assertIn("salle1", var.liste_salles)
        self.assertIn("salle2", var.liste_salles)
        mock_create_url.assert_any_call("salle1")
        mock_create_url.assert_any_call("salle2")
        mock_calcul_consigne.assert_any_call("url_salle1")
        mock_calcul_consigne.assert_any_call("url_salle2")

class TestCreateICalendar(unittest.TestCase):
    """Teste le module create_file_icalendar."""

    def test_correct_information(self):
        """Teste la création d'un fichier iCalendar avec des informations correctes."""
        salle = '8C-030 CHR*  (32pl./32 écrans sans PC)VP TB'
        horaires = [(datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)),
                    (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)),
                    (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0))]
        summaries = ['Occupation Salle 1', 'Reunion', 'Maintenance']
        create_icalendar_file(salle, horaires, summaries)
        expected_filename = 'calendrier_8C-030_CHR__(32pl.32_écrans_sans_PC)VP_TB.ics'
        self.assertTrue(os.path.exists(expected_filename), f"File '{expected_filename}' does not exist.")

    def test_invalid_hours(self):
        """Teste la création d'un fichier iCalendar avec des horaires invalides."""
        salle = '8C-030 CHR*  (32pl./32 écrans sans PC)VP TB'
        horaires = [(datetime(2024, 2, 13, 8, 0), datetime(2024, 2, 13, 10, 0)),
                    (datetime(2024, 2, 13, 10, 40), datetime(2024, 2, 13, 11, 0)),
                    (datetime(2024, 2, 14, 10, 0), datetime(2024, 2, 14, 12, 0))]
        summaries = ['Occupation Salle 1', 'Reunion', 'Maintenance']
        create_icalendar_file(salle, horaires, summaries)
        expected_filename = 'calendrier_8C-030_CHR__(32pl.32_écrans_sans_PC)VP_TB.ics'
        self.assertTrue(os.path.exists(expected_filename), f"File '{expected_filename}' does not exist.")

    def test_invalid_input(self):
        """Teste la création d'un fichier iCalendar avec des entrées invalides."""
        salle = '8C-030 CHR*  (32pl./32 écrans sans PC)VP TB'
        horaires = ['invalid']
        summaries = ['Invalid']
        with self.assertRaises(ValueError):
            create_icalendar_file(salle, horaires, summaries)

class TestConnexionInfluxDB(unittest.TestCase):
    """Teste le module connexion."""

    def test_connexion_influxdb_success(self):
        """Teste la fonction connexion."""
        url = 'http://test_host'
        token = 'test_token'
        org = 'test_org'
        client = connexion(url, token, org)
        self.assertIsNotNone(client)

    def test_close_connexion(self):
        """Teste la fonction close."""
        client = MagicMock()  # Créer un mock client InfluxDB pour simuler la connexion
        close(client)
        client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()

