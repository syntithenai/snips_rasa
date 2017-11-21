from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from typing import Any
from typing import Dict
from typing import List
from typing import Text

from rasa_nlu.emulators import NoEmulator


class SnipsEmulator(NoEmulator):
    def __init__(self):
        # type: () -> None

        super(SnipsEmulator, self).__init__()
        self.name = "snips"

    def normalise_response_json(self, data):
        # type: (Dict[Text, Any]) -> List[Dict[Text, Any]]
        """Transform data to wit.ai format."""


        slots=[]
                    
        for entity in data['entities']:
            slot = {"entity": entity['value'],"range": {"end": entity['end'],"start": entity['start']},"rawValue": entity['value'],"slotName": "entity","value": {"kind": "Custom","value": entity['value']}} 
            slots.append(slot)
        
        intentName = "user_Kr5A7b4OD__{}".format(data['intent']['name'])
        return {"input": data["text"],"intent": {"intentName": intentName,"probability": 1.0},"slots": slots} 
