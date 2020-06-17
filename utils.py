import requests
import json

def to_discwebhook(message: str, url: str, embed: dict = {}, force: bool = False) -> str:
    content = '{"content": $msg_content}'
    content.replace('$msg_content', f'"{message}"')
    header = {'Content-Type': 'application/json'}
    data = {}
    if message is not None:
        data["content"] = message
    data["embeds"] = []
    data["embeds"].append(embed) if len(embed) else {}
    result = requests.post(url=url, data=json.dumps(data), headers=header)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        return {
            'message': "Sent to Discord succesfully code {}.".format(result.status_code),
            'response': result
        }
