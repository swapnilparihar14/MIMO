# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher

from .database_connectivity import DBConnection
from .txt2emo import get_emotion
from .utility import check_good_weather


from rasa_sdk.forms import FormValidationAction


class ValidateFormFeelings(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_ask_feelings"

    async def extract_feelings(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):

        return [SlotSet("feelings",tracker.latest_message.get("text"))]


class ActionExtractEmotion(Action):

    def name(self) -> Text:
        return "action_extract_emotion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        last_message = tracker.latest_message.get("text")
        result = get_emotion(last_message)
        winner = max(result, key=result.get).lower()
        if winner == 'surprise':
            text = f'You seem surprised and shocked by this. \n' \
                   f'Would you like to read a book? \n OR \n' \
                   f'How about we do some yoga?'
        elif winner == 'fear':
            text = f'You seem scared, please call 911 if you need assistance. \n'\
                   f'Would you like to read a book? \n OR \n' \
                   f'Would you like to see cute animal pictures?'

        elif winner == 'sad':
            text = f"You definitely seem sad and that's a sign of depression.\n" \
                   f"Would you like to see cute animal pictures?'\n OR \n" \
                   f"Go for a walk to clear your mind ?"
        elif winner == 'angry':
            text = f"You seemed angry and can benifit from professional expert's help.\n " \
                   f"How about we do some yoga? \n OR \n Go for a walk to clear your mind ??"
        else:
            text = f'I think you are you are going through somethings but you will be okay.' \
                   f' \n Still would you like to contact a medical professional to discuss this further in person?'

        dispatcher.utter_message(text=text)
        return []


class VerifyUserCity(Action):

    def name(self) -> Text:
        return "action_verify_city"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        anonymity = tracker.get_slot('anonymity')
        email = tracker.get_slot('email')
        A = DBConnection()
        if anonymity == "Yes":
            return [FollowupAction("utter_options")]
        records = A.get_patient_records(email)
        if records is None or 'address' not in records:
            return []
        return [SlotSet("city", records['address'] if records['address'] is not None else "")]


class VerifyUserName(Action):

    def name(self) -> Text:
        return "action_verify_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        anonymity = tracker.get_slot('anonymity')
        email = tracker.get_slot('email')
        A = DBConnection()
        if anonymity == "Yes":
            return [FollowupAction("utter_options")]
        records = A.get_patient_records(email)
        if records is None or 'patient_name' not in records:
            return []

        return [SlotSet("name", records['patient_name'] if records['patient_name'] is not None else "")]


class VerifyUserPhone(Action):

    def name(self) -> Text:
        return "action_verify_phone"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        anonymity = tracker.get_slot('anonymity')
        email = tracker.get_slot('email')
        A = DBConnection()
        if anonymity == "Yes":
            return [FollowupAction("utter_options")]
        records = A.get_patient_records(email)
        if records is None or 'phone' not in records:
            return []
        return [SlotSet("phone_number", records['phone'] if records['phone'] is not None else "")]


class AddUser(Action):

    def name(self) -> Text:
        return "action_add_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        anonymity = tracker.get_slot('anonymity')
        email = tracker.get_slot('email')
        phone = tracker.get_slot('phone_number')
        address = tracker.get_slot('city')
        patient_name = tracker.get_slot('name')
        A = DBConnection()
        if anonymity == "Yes":
            return [FollowupAction("utter_request")]
        records = A.get_patient_records(email)
        if records is None:
            A.add_patient_info(email, phone, patient_name, address)
        return []


class GetDoctorData(Action):
    def name(self) -> Text:
        return "action_get_doctor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        city = tracker.get_slot('city')
        if city is None:
            return [FollowupAction("utter_city")]
        A = DBConnection()
        dispatcher.utter_message(text=A.get_doctor_info(city))
        return []


class UpdateWalkData(Action):
    def name(self) -> Text:
        return "action_update_walk"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            A.increment_patient_variables(email, 'walk')
        return []


class UpdatePhotoData(Action):
    def name(self) -> Text:
        return "action_update_photo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            A.increment_patient_variables(email, 'photos')
        return []


class UpdateReadData(Action):
    def name(self) -> Text:
        return "action_update_read"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            A.increment_patient_variables(email, 'reading')
        return []


class UpdateYogaData(Action):
    def name(self) -> Text:
        return "action_update_yoga"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            A.increment_patient_variables(email, 'yoga')
        return []

class WalkWeather(Action):
    def name(self) -> Text:
        return "action_walk_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        city = tracker.get_slot('city')
        if city is None:
            return [FollowupAction("utter_city")]
        result = check_good_weather(city)
        if result == 0:
            text = "I am unable to check the weather at your location. If its good enough, how about we go for a walk?"
        elif result == 1:
            text = f"The weather seems good in {city}. Fresh air and smiling faces ought to make you feel good." \
                   " How about we go for a walk?"
        else:
            text = f"I can understand that the weather is not that good in {city}. " \
                   f"How about I show you cute animal picks or we do yoga or we read a book?"
        dispatcher.utter_message(text=text)
        return []


class CheckWeather(Action):
    def name(self) -> Text:
        return "action_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        city = tracker.get_slot('city')
        if city is None:
            return [FollowupAction("utter_city")]
        result = check_good_weather(city)
        if result == 0:
            text = "I am unable to check the weather at your location."
        elif result == 1:
            text = f"The weather seems good in {city}"
        else:
            text = f"The weather is not that good in {city}"
        dispatcher.utter_message(text=text)
        return []


class GetYogaData(Action):
    def name(self) -> Text:
        return "action_get_yoga"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            dispatcher.utter_message(text="Details Not found")
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            records = A.get_patient_records(email)
            dispatcher.utter_message(text=f"Yoga: {records['yoga']}")
        else:
            dispatcher.utter_message(text="Details Not found")
        return []


class GetPhotoData(Action):
    def name(self) -> Text:
        return "action_get_photo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            dispatcher.utter_message(text="Details Not found")
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            records = A.get_patient_records(email)
            dispatcher.utter_message(text=f"Photo: {records['photos']}")
        else:
            dispatcher.utter_message(text="Details Not found")
        return []


class GetWalkData(Action):
    def name(self) -> Text:
        return "action_get_walk"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            dispatcher.utter_message(text="Details Not found")
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            records = A.get_patient_records(email)
            dispatcher.utter_message(text=f"Walking: {records['walk']}")
        else:
            dispatcher.utter_message(text="Details Not found")
        return []


class GetReadData(Action):
    def name(self) -> Text:
        return "action_get_read"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        anonymity = tracker.get_slot('anonymity')
        if anonymity == "Yes":
            dispatcher.utter_message(text="Details Not found")
            return []
        email = tracker.get_slot('email')
        if email is not None:
            A = DBConnection()
            records = A.get_patient_records(email)
            dispatcher.utter_message(text=f"Reading: {records['reading']}")
        else:
            dispatcher.utter_message(text="Details Not found")
        return []