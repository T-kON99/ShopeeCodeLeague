import base64
from datetime import datetime, timezone
from GoogleMail import GoogleMail
import secrets as secrets
import utils as utils
import time
import re
import config as conf
import json

time_list = {
    'SGT': '+0700'
}

def get_date_shopee(date_string: str):
    return datetime.strptime(date_string, '%d %b %Y, %A %I:%M%p %z')

def main():
    app = GoogleMail('./credentials.json')
    all_valid_events = []
    all_messages = app.list_('messages', {'q': 'from: techsg@shopee.com '})
    for message in all_messages:
        event_details = {}
        email_message = app.get_('messages', {'id': message['id']})
        headers = email_message['payload']['headers']
        subject = [_['value'] for _ in headers if _['name'] == 'Subject'][0]
        print(f'Fetching {subject}...')
        if str(subject).startswith('[Confirmation]'):
            b64_body_content = email_message['payload']['parts'][0]
            try:
                decoded_body_content = base64.urlsafe_b64decode(b64_body_content['body']['data'].encode('ASCII'))
                filtered = [_.decode() for _ in decoded_body_content.strip().split(b'\r\n')[0:-1] if len(_)]
                event_name, event_creator, *_ = subject.lstrip('[Confirmation]').strip().split('by')
                event_organizer, *_ = [_.strip() for _ in event_creator.split('on')]
                event_details['title'] = event_name.strip()
                event_details['organizer'] = event_organizer
                for sentence in filtered:
                    if sentence.startswith('Date'):
                        event_details['date'] = sentence.lstrip('Date:').strip()
                    elif sentence.startswith('Time'):
                        event_details['time'] = sentence.lstrip('Time:').strip()
                    elif sentence.startswith('Platform'):
                        event_details['platform'] = sentence.lstrip('Platform:').strip()
                    else:
                        for digit in range(10):
                            if sentence.startswith(str(digit)):
                                step = sentence.lstrip(str(digit) + '.').strip()
                                try:
                                    event_details['step'].append(step)
                                except KeyError:
                                    event_details['step'] = [step]
                                break
                start_time, end_time_sgt = event_details['time'].split('-')
                end_time, region = end_time_sgt.split(' ')
                region = time_list[region.strip('()')]
                event_start = f'{event_details["date"]} {start_time} {region}'
                event_end = f'{event_details["date"]} {end_time} {region}'
                event_details['start'] = event_start
                event_details['end'] = event_end
                if get_date_shopee(event_end) >= datetime.now(timezone.utc):
                    all_valid_events.append(event_details)
            except Exception as err:
                print(f'[ERROR]: {err} on subject {subject}')
                input('XX')
    return all_valid_events

if __name__ == '__main__':
    all_events = main()
    with open('./announced.json', mode='r') as file:
        announced_events = json.load(file)
    for event in sorted(all_events, key=lambda x: x['start']):
        if f"{event['title']}{event['date']}" in announced_events:
            continue
        announced_events[f"{event['title']}{event['date']}"] = event
        url_regex = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
        zoom_link = [_.strip('()') for _ in event['step'][0].split(' ') if _.startswith('(')][0]
        meeting_id = event['step'][4].split('"')[1]
        meeting_pwd = event['step'][5].lstrip('Webinar Password:').strip()
        preparation_raw = event['step'][6:]
        preparation_processed = []
        for step in preparation_raw:
            processed = []
            for index, word in enumerate(step.split(' ')):
                if word.startswith('(') and word.endswith(')') and re.match(url_regex, word.strip('()')) is not None:
                    if index > 0:
                        processed[-1] = f'[{processed[-1]}]{word}'
                    else:
                        processed.append(word)
                else:
                    processed.append(word)
            preparation_processed.append(' '.join(processed))
        discord_embed = {
            'title': event['title'],
            'description': f'{event["date"]} {event["time"]}',
            'author': {
                'name': event['organizer'],
                'url': conf.WORKSHOP_ORGANIZER.get("".join((_.lower() for _ in event["organizer"].split(" "))), {'url': 'https://zoom.us/'})['url'],
                'icon_url': conf.WORKSHOP_ORGANIZER.get("".join((_.lower() for _ in event["organizer"].split(" "))), {'icon': 'https://blog.huddlecamhd.com/wp-content/uploads/2015/11/zoom-logo-circle.webp'})['icon']
            },
            'url': zoom_link,
            'fields': [
                {
                    'name': 'Platform',
                    'value': f'**{event["platform"]}**'
                },
                {
                    'name': 'Meeting ID',
                    'value': f'**{meeting_id}**'
                },
                {
                    'name': 'Meeting Password',
                    'value': f'**{meeting_pwd}**'
                },
                {
                    'name': 'Preparation',
                    'value': '\n\n'.join([f'**{i + 1}**. {sentence}' for i, sentence in enumerate(preparation_processed)]) if len(preparation_processed) else '-'
                },
            ],
            'footer': {
                'text': 'Shopee Code League #2020'
            },
            'color': 0x54ed4e,
            'image': {
                'url': 'https://careers.shopee.sg/codeleague/images/codeleague-cover.jpg'
            }
        }
        print(discord_embed)
        response = utils.to_discwebhook(None, secrets.DISCORD_WEBHOOK, discord_embed)
        time.sleep(1)
        print(response)
    
    with open('./announced.json', mode='w') as file:
        json.dump(announced_events, file)