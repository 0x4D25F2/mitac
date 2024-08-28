import re
import json
import math


class ADOFAI:
    def __init__(self):
        with open(r"./base.adofai", "r", encoding="utf-8") as f:
            s = f.read()[1:]
        
        s = re.sub(r",\s+]", "]", s)
        self._c = json.loads(s)
    
    def __len__(self):
        return len(self._c["angleData"])
    
    def set_metadata(self, name, value):
        self._c["settings"][name] = value
    
    def get_metadata(self, name):
        return self._c["settings"][name]
    
    def get_event(self, floor: int, type: str):
        if floor <= -1:
            floor = len(self) + floor + 1
        for i in self._c["actions"]:
            if i["floor"] == floor and i["eventType"] == type:
                return i
        return None
    
    def set_speed_bpm(self, floor: int, bpm, override: bool = False):
        if floor <= -1:
            floor = len(self) + floor + 1
        if override:
            a = self.get_event(floor, "SetSpeed")
            if a:
                self._c["actions"].remove(a)
        self._c["actions"].append(
            {"floor": floor, "eventType": "SetSpeed", "speedType": "Bpm", "beatsPerMinute": bpm, "bpmMultiplier": 1,
             "angleOffset": 0})
    
    def set_speed_multi(self, floor: int, multiple):
        self._c["actions"].append(
            {"floor": floor, "eventType": "SetSpeed", "speedType": "Multiplier", "beatsPerMinute": 100,
             "bpmMultiplier": multiple,
             "angleOffset": 0})
    
    def get_last_angle(self):
        if len(self._c["angleData"]) == 0:
            return 0
        ad = self._c["angleData"][-1]
        if ad != 999:
            return ad
        else:
            return self._c["angleData"][-2]
    
    def add_angle_data(self, value, midspin: bool = False):
        self._c["angleData"].append(value % 360)
        if midspin:
            self._c["angleData"].append(999)
    
    def add_twirl(self, floor: int, is_check: bool = False):
        if floor <= -1:
            floor = len(self) + floor + 1
        if is_check:
            if {"floor": floor, "eventType": "Twirl"} in self._c["actions"]:
                self._c["actions"].remove({"floor": floor, "eventType": "Twirl"})
                return
        self._c["actions"].append({"floor": floor, "eventType": "Twirl"})
    
    def add_pause(self, floor: int, time):
        if floor <= -1:
            floor = len(self) + floor + 1
        self._c["actions"].append(
            {"floor": floor, "eventType": "Pause", "duration": time, "countdownTicks": 0, "angleCorrectionDir": 0})
    
    def lag_handle(self, appearDist, disappearDist):
        self._c["actions"].append(
            {"floor": 0, "eventType": "MoveTrack", "startTile": [appearDist, "Start"], "endTile": [0, "End"],
             "gapLength": 0, "duration": 1, "positionOffset": [9999, 9999], "angleOffset": 0, "ease": "Linear",
             "maxVfxOnly": False, "eventTag": ""})
        for i in range(len(self._c["angleData"])):
            self._c["actions"].append({"floor": i, "eventType": "MoveTrack", "startTile": [appearDist, "ThisTile"],
                                       "endTile": [appearDist, "ThisTile"], "gapLength": 0, "duration": 0,
                                       "positionOffset": [0, 0], "angleOffset": 0, "ease": "Linear",
                                       "maxVfxOnly": False, "eventTag": ""})
            if i >= disappearDist:
                self._c["actions"].append(
                    {"floor": i, "eventType": "MoveTrack", "startTile": [0 - disappearDist, "ThisTile"],
                     "endTile": [0 - disappearDist, "ThisTile"], "gapLength": 0, "duration": 1,
                     "positionOffset": [9999, 9999], "angleOffset": 0, "ease": "Linear", "maxVfxOnly": False,
                     "eventTag": ""})
    
    def save(self, path: str):
        # 适配了一下ADOPAC 所以代码看起来not good
        for i in range(len(self)):
            v = self._c["angleData"][i]
            v = 999 if v == 999 else v % 360
            if v % 1 >= 1e-5:
                v = round(v, 7 - len(str(v % 360).split(".")[0]))
            else:
                v = int(v)
            self._c["angleData"][i] = v
        with open(path, "w", encoding="utf_8_sig") as f:
            f.write("{\"angleData\": "+str(self._c["angleData"])+",")
            tx = json.dumps({"settings": self._c["settings"], "actions": self._c["actions"]}, indent="\t")[1:]
            f.write(tx.replace("\n\t\t\t", "").replace("\n\t\t]", "]").replace("\n\t\t}", "}"))
