import subprocess
from colorama import Fore, init
import os

init()

check = False

def get_network_adapters() -> list:
    try:
        result = subprocess.run(['ls', '/sys/class/net/'], capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Ошибка при получении списка сетевых адаптеров: {e}{Fore.RESET}")
        return []

def display_adapters(adapters) -> None:
    for i, adapter in enumerate(adapters):
        print(f"[{Fore.GREEN}{i}{Fore.RESET}] {Fore.CYAN}{adapter}{Fore.RESET}")

def get_user_choice(adapters) -> str:
    try: 
        while True:
            choice = input(f"{Fore.LIGHTRED_EX}Выберите один из адаптеров: {Fore.RESET}")
            if choice.isdigit() and 0 <= int(choice) < len(adapters):
                return adapters[int(choice)]
            elif choice in adapters:
                return choice
            else:
                print(f"{Fore.RED}\n\nЭтого адаптера нет в списке!\n\n{Fore.RESET}")
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[CTRL+C detected]{Fore.RESET}")
        

def main():
    global check
    try:
        if os.getuid() == 0:
            adapters = get_network_adapters()
            if not adapters:
                print(f"{Fore.RED}Нет доступных сетевых адаптеров.{Fore.RESET}")
                return

            display_adapters(adapters)
            chosen_adapter = get_user_choice(adapters)
            if chosen_adapter != None:
                print(f"Выбранный адаптер: {Fore.CYAN}{chosen_adapter}{Fore.RESET}")
            
                print(f"Перевод адаптера в режим монитора...")
                subprocess.run(['airmon-ng','start', chosen_adapter], capture_output=True, text=True, check=True)
                check = True
                path_to_file = input("Введите пожалуйста полный путь до словаря с названиями WiFi: ")
                if os.path.isfile(path_to_file):
                    print(f"{Fore.RED}Точки WiFi успешно созданы! Для выхода удаления нажмите CTRL+C{Fore.RESET}")
                    subprocess.run(['mdk3', f'{chosen_adapter}mon','b','-c','1','-f', path_to_file], capture_output=True, text=True, check=True)
                else:
                    print('\n\nТакого файла не существует!\n\n')
                    subprocess.run(['airmon-ng','stop',f'{chosen_adapter}mon'], capture_output=True, text=True, check=True)
                    main()
            
        else:
            print("Пожалуйста, запустите программу с правами супер пользователя!")
            return 0
    except KeyboardInterrupt:
        if check and chosen_adapter[-3::] != 'mon':
            subprocess.run(['airmon-ng','stop',f'{chosen_adapter}mon'], capture_output=True, text=True, check=True)
        else:
            subprocess.run(['airmon-ng','stop',f'{chosen_adapter}'], capture_output=True, text=True, check=True)
        print(f"\n\n{Fore.RED}[CTRL+C detected]{Fore.RESET}")

if __name__ == "__main__":
    main()

