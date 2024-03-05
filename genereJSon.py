import base64
import json

def base10_to_base64(num):
    # Converti le nombre en bytes
    byte_representation = int.to_bytes(num, (num.bit_length() + 7) // 8, 'big')

    # Encode en base64
    base64_encoded = base64.b64encode(byte_representation)

    # Décode les bytes en une chaîne de caractères
    base64_string = base64_encoded.decode('utf-8')

    return base64_string

def genereJSon(temp):
    # Converti la température en base64
    temp_en_base64 = base10_to_base64(temp)

    # Créer le dictionnaire JSON
    json_data = {
        "downlinks": [{
            "f_port": 15,
            "frm_payload": temp_en_base64,
            "priority": "NORMAL"
        }]
    }

    json_string = json.dumps(json_data, indent=2)

    return json_string

# Exemple d'utilisation
temp_en_base_10 = 20
json_result = genereJSon(temp_en_base_10)

print(f"Température en base 10: {temp_en_base_10}")
print("JSON généré:")
print(json_result)
