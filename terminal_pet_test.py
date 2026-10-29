import json
import os
import random
import time

SAVE_FILE = "pet_save.json"


class Pet:
    """애완동물 상태 및 행동 관리 클래스"""

    def __init__(self, name, species, hunger=70, mood=70, energy=70, last_time=None):
        self.name = name
        self.species = species
        self.hunger = hunger
        self.mood = mood
        self.energy = energy
        self.last_time = last_time if last_time else time.time()

    def clamp_stats(self):
        """수치를 0~100 범위로 제한"""
        self.hunger = max(0, min(100, self.hunger))
        self.mood = max(0, min(100, self.mood))
        self.energy = max(0, min(100, self.energy))

    def apply_offline_decay(self):
        """종료 후 지난 시간만큼 상태 감소"""
        elapsed = time.time() - self.last_time
        if elapsed < 5:
            return

        minutes, hours = int(elapsed // 60), int(elapsed // 3600)
        time_str = f"{hours}시간" if hours >= 1 else (f"{minutes}분" if minutes >= 1 else f"{int(elapsed)}초")
        print(f"\n[안내] {self.name}가 {time_str} 동안 기다렸어요!")

        decay = (minutes // 10) * 2  # 10분당 배부름/기분 -2, 체력 -1
        if decay > 0:
            self.hunger -= decay
            self.mood -= decay
            self.energy -= decay // 2
            self.clamp_stats()
            print(f"기다리는 동안 배부름(-{decay}), 기분(-{decay}), 체력(-{decay // 2})이 감소했습니다.")

    def feed(self):
        """밥 주기: 배부르면 거부"""
        if self.hunger >= 90:
            print(f"\n{self.name}: 배가 이미 빵빵해서 더 못 먹어요! ({self.hunger}/100)")
            return
        self.hunger += 25
        self.clamp_stats()
        print(f"\n{self.name}에게 맛있는 밥을 주었습니다! (배부름 +25)")

    def play(self):
        """놀아 주기: 가위바위보 미니게임 (피곤하면 거부)"""
        if self.energy <= 20:
            print(f"\n{self.name}: 너무 피곤해서 놀 수 없어요... 먼저 잠을 재워주세요!")
            return

        choices = {"1": "가위", "2": "바위", "3": "보"}
        print(f"\n[{self.name}와(과)의 가위바위보 대결!]")
        choice = input("1. 가위  2. 바위  3. 보  >> ").strip()
        if choice not in choices:
            print("[안내] 1, 2, 3 중에서 골라주세요.")
            return

        user_pick, pet_pick = choices[choice], random.choice(["가위", "바위", "보"])
        print(f"\n나: {user_pick}  vs  {self.name}: {pet_pick}")

        if user_pick == pet_pick:
            print("비겼습니다! 박빙의 승부였어요! (기분 +15)")
            self.mood += 15
        elif (user_pick, pet_pick) in [("가위", "보"), ("바위", "가위"), ("보", "바위")]:
            print(f"당신이 이겼습니다! {self.name}가 신나게 뜁니다! (기분 +30)")
            self.mood += 30
        else:
            print(f"{self.name}가 이겼습니다! 즐거운 시간이었어요! (기분 +20)")
            self.mood += 20

        self.energy -= 15
        self.hunger -= 10
        self.clamp_stats()
        print("(체력 -15, 배부름 -10)")

    def sleep(self):
        """재우기: 체력 회복"""
        self.energy += 40
        self.hunger -= 5
        self.clamp_stats()
        print(f"\n{self.name}가 쿨쿨 낮잠을 잤습니다. (체력 +40, 배부름 -5)")

    def natural_decay(self):
        """행동 후 자연 상태 감소"""
        self.hunger -= 2
        self.mood -= 2
        self.clamp_stats()

    def get_face(self):
        """상태에 따른 표정 반환 (좋음 ^.^, 보통 o.o, 나쁨 T.T)"""
        avg = (self.hunger + self.mood + self.energy) / 3
        if min(self.hunger, self.mood, self.energy) <= 20 or avg < 40:
            return "T.T"
        return "^.^" if avg >= 70 else "o.o"

    def print_status(self):
        """ASCII 표정 및 상태 막대 표시"""
        face = self.get_face()
        art = f"  /^ ^\\\n ( {face} )\n  ∪   ∪ " if self.species == "강아지" else f"  /\\_/\\\n ( {face} )\n  > ^ < "

        def bar(val):
            filled = val // 10
            return f"[{'■' * filled}{'□' * (10 - filled)}] {val:>3}/100"

        print("\n" + "=" * 36 + f"\n[{self.species}] {self.name}\n{art}\n" + "-" * 36)
        print(f"배부름: {bar(self.hunger)}\n기  분: {bar(self.mood)}\n체  력: {bar(self.energy)}")
        print("-" * 36)

        if self.hunger <= 20:
            print("⚠️  [경고] 배가 많이 고파요! 밥을 주세요!")
        if self.mood <= 20:
            print("⚠️  [경고] 심심하고 외로워해요! 같이 놀아주세요!")
        if self.energy <= 20:
            print("⚠️  [경고] 체력이 부족해요! 잠을 재워주세요!")
        print("=" * 36)

    def to_dict(self):
        return {"name": self.name, "species": self.species, "hunger": self.hunger,
                "mood": self.mood, "energy": self.energy, "last_time": time.time()}


def save_pet(pet):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(pet.to_dict(), f, ensure_ascii=False, indent=2)


def load_pet():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            return Pet(d["name"], d["species"], d["hunger"], d["mood"], d["energy"], d.get("last_time"))
    except Exception:
        return None


def create_new_pet():
    print("\n" + "=" * 36 + "\n    🌟 새 애완동물 입양하기 🌟\n" + "=" * 36)
    name = ""
    while not name:
        name = input("애완동물의 이름을 지어주세요: ").strip()

    while True:
        choice = input("종류를 선택하세요 (1. 고양이, 2. 강아지): ").strip()
        if choice in ["1", "2"]:
            species = "고양이" if choice == "1" else "강아지"
            break
        print("[안내] 1 또는 2를 입력해주세요.")

    print(f"\n축하합니다! 귀여운 {species} '{name}'을(를) 만났습니다!")
    return Pet(name, species)


def main():
    print("=" * 36 + "\n   🐾 터미널 애완동물 키우기 🐾\n" + "=" * 36)
    pet = load_pet()
    if pet:
        print(f"\n저장된 {pet.species} '{pet.name}'의 정보를 불러왔습니다.")
        pet.apply_offline_decay()
    else:
        pet = create_new_pet()
        save_pet(pet)

    while True:
        pet.print_status()
        print("1. 밥 주기\n2. 놀아 주기 (가위바위보)\n3. 재우기\n4. 저장하고 종료")
        cmd = input("행동을 선택하세요 (1~4): ").strip()

        if cmd == "1":
            pet.feed()
        elif cmd == "2":
            pet.play()
        elif cmd == "3":
            pet.sleep()
        elif cmd == "4":
            save_pet(pet)
            print(f"\n{pet.name}: 다음에 또 봐요! 안녕~ 🐾\n게임이 저장되고 종료되었습니다.")
            break
        else:
            print("\n[안내] 잘못된 입력입니다. 1~4 중에서 선택해주세요.")
            continue
        pet.natural_decay()


if __name__ == "__main__":
    main()




