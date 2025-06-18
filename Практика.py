import random
import tkinter as tk
from tkinter import messagebox

class Resource:
    def __init__(self, name, resource_type, value, humidity_sensitive=False, food=False):
        self._name = name
        self._type = resource_type
        self._value = value
        self._damaged = False
        self._humidity_sensitive = humidity_sensitive
        self._food = food

    def get_info(self):
        status = "+" if not self._damaged else "-"
        return f"{status} {self._name} ({self._type}) - {self._value}₽"

class Pest:
    def __init__(self, name, damage_chance, spawn_conditions, affected_types):
        self._name = name
        self._damage_chance = damage_chance
        self._spawn_conditions = spawn_conditions
        self._affected_types = affected_types
        self._active = False

    def check_spawn_conditions(self, warehouse):
        if 'required_resources' in self._spawn_conditions:
            required = self._spawn_conditions['required_resources']
            if not any(r._type in required for r in warehouse._resources):
                return False

        if 'damaged_resources' in self._spawn_conditions:
            min_damaged = self._spawn_conditions['damaged_resources']
            if len([r for r in warehouse._resources if r._damaged]) < min_damaged:
                return False

        if 'min_day' in self._spawn_conditions:
            if warehouse._day < self._spawn_conditions['min_day']:
                return False

        return True

    def try_damage(self, resource):
        if resource._type in self._affected_types and not resource._damaged and self._active:
            if random.random() < self._damage_chance:
                resource._damaged = True
                return True
        return False

class Poison:
    def __init__(self, name, effectiveness, cost):
        self._name = name
        self._effectiveness = effectiveness
        self._cost = cost
        self._owned = 0

    def try_kill(self, pest):
        if self._owned <= 0:
            return False

        kill_chance = self._effectiveness.get(pest._name, 0.0)
        success = random.random() < kill_chance
        if success:
            self._owned -= 1
        return success

class RandomEvent:
    def __init__(self, name, description, probability, effect):
        self._name = name
        self._description = description
        self._probability = probability
        self._effect = effect

    def check_event(self, warehouse):
        return random.random() < self._probability

class WarehouseGame:
    def __init__(self, root):
        self._root = root
        self._root.title("Борьба с вредителями на складе")
        self._root.configure(bg='#B1E0F2')

        self._resources = []
        self._pests = []
        self._poisons = []
        self._random_events = []
        self._money = 1000
        self._day = 0
        self._humidity = 30
        self._security_level = 2

        self.create_resources()
        self.create_pests()
        self.create_poisons()
        self.create_events()

        self.setup_ui()

    def setup_ui(self):
        self._top_frame = tk.Frame(self._root, bg='#B1E0F2')
        self._top_frame.pack(pady=10)

        self._middle_frame = tk.Frame(self._root, bg='#B1E0F2')
        self._middle_frame.pack(pady=10)

        self._bottom_frame = tk.Frame(self._root, bg='#B1E0F2')
        self._bottom_frame.pack(pady=10)

        self._info_label = tk.Label(self._top_frame,
                                   text=f"День: {self._day} | Деньги: {self._money}₽ | Влажность: {self._humidity}% | Безопасность: {'★'*self._security_level}",
                                   font=('Arial', 12), bg='#B1E0F2')
        self._info_label.pack()

        self._resources_label = tk.Label(self._middle_frame, text="Ресурсы на складе:",
                                       font=('Arial', 12), bg='#B1E0F2')
        self._resources_label.pack(anchor='w')

        self._resources_listbox = tk.Listbox(self._middle_frame, width=70, height=8,
                                           bg='white', fg='black', selectbackground='#A4D8F2')
        self._resources_listbox.pack()
        self.update_resources_list()

        self._pests_label = tk.Label(self._middle_frame, text="Активные вредители:",
                                    font=('Arial', 12), bg='#B1E0F2')
        self._pests_label.pack(anchor='w', pady=(10, 0))

        self._pests_listbox = tk.Listbox(self._middle_frame, width=70, height=3,
                                        bg='white', fg='black', selectbackground='#A4D8F2')
        self._pests_listbox.pack()
        self.update_pests_list()

        self._inventory_label = tk.Label(self._middle_frame, text="Ваши средства:",
                                       font=('Arial', 12), bg='#B1E0F2')
        self._inventory_label.pack(anchor='w', pady=(10, 0))

        self._inventory_listbox = tk.Listbox(self._middle_frame, width=70, height=3,
                                           bg='white', fg='black', selectbackground='#A4D8F2')
        self._inventory_listbox.pack()
        self.update_inventory_list()

        button_style = {'width':15, 'bg':'#7FB3D5', 'activebackground':'#5D8BF4',
                       'fg':'white', 'font':('Arial', 10)}

        self._next_day_btn = tk.Button(self._bottom_frame, text="Следующий день",
                                      command=self.next_day, **button_style)
        self._next_day_btn.pack(side='left', padx=5)

        self._buy_poison_btn = tk.Button(self._bottom_frame, text="Купить средство",
                                        command=self.buy_poison_menu, **button_style)
        self._buy_poison_btn.pack(side='left', padx=5)

        self._use_poison_btn = tk.Button(self._bottom_frame, text="Использовать средство",
                                        command=self.use_poison_menu, **button_style)
        self._use_poison_btn.pack(side='left', padx=5)

        self._repair_btn = tk.Button(self._bottom_frame, text="Починить ресурсы",
                                    command=self.repair_resources_menu, **button_style)
        self._repair_btn.pack(side='left', padx=5)

        self._manage_btn = tk.Button(self._bottom_frame, text="Управление складом",
                                    command=self.manage_warehouse, **button_style)
        self._manage_btn.pack(side='left', padx=5)

    def create_resources(self):
        resources = [
            ("Мука", "продукты", 50, True, True),
            ("Сахар", "продукты", 40, True, True),
            ("Мыло", "бытовая химия", 30, False, False),
            ("Доски", "стройматериалы", 80, True, False),
            ("Краска", "стройматериалы", 120, False, False),
            ("Консервы", "продукты", 60, False, True),
            ("Гвозди", "стройматериалы", 30, False, False),
            ("Крупа", "продукты", 45, True, True)
        ]
        for name, r_type, value, hum, food in resources:
            self._resources.append(Resource(name, r_type, value, hum, food))

    def create_pests(self):
        pests = [
            ("Крысы", 0.3,
             {"required_resources": ["продукты"], "damaged_resources": 1, "min_day": 0},
             ["продукты", "бытовая химия"]),
            ("Тараканы", 0.2,
             {"required_resources": ["продукты"], "min_day": 2},
             ["продукты"]),
            ("Плесень", 0.4,
             {"required_resources": ["стройматериалы"], "min_day": 3, "humidity": 50},
             ["стройматериалы"]),
            ("Мыши", 0.25,
             {"damaged_resources": 2, "min_day": 5},
             ["продукты"])
        ]
        for name, chance, conditions, types in pests:
            self._pests.append(Pest(name, chance, conditions, types))

    def create_poisons(self):
        poisons = [
            ("Яд для грызунов", {"Крысы": 0.8, "Мыши": 0.7}, 100),
            ("Инсектицид", {"Тараканы": 0.9}, 80),
            ("Антисептик", {"Плесень": 0.85}, 120),
            ("Универсальное средство", {"Крысы": 0.5, "Тараканы": 0.6, "Плесень": 0.4, "Мыши": 0.5}, 150)
        ]
        for name, effectiveness, cost in poisons:
            self._poisons.append(Poison(name, effectiveness, cost))

    def create_events(self):
        events = [
            ("Кража", "Воры проникли на склад и украли часть товаров!", 0.1,
             lambda w: w.steal_resources(random.randint(1, 3))),
            ("Пожар", "На складе случился пожар! Часть товаров повреждена.", 0.05,
             lambda w: w.fire_damage()),
            ("Наводнение", "Из-за протечки повысилась влажность и часть товаров испорчена.", 0.07,
             lambda w: w.flood_damage()),
            ("Удачный день", "Сегодня хорошие продажи!", 0.1,
             lambda w: w.add_money(random.randint(50, 200))),
            ("Проверка", "Проверка выявила недостачу. Штраф!", 0.08,
             lambda w: w.add_money(-random.randint(50, 150)))
        ]
        for name, desc, prob, effect in events:
            self._random_events.append(RandomEvent(name, desc, prob, effect))

    def update_resources_list(self):
        self._resources_listbox.delete(0, tk.END)
        for resource in self._resources:
            self._resources_listbox.insert(tk.END, resource.get_info())

    def update_pests_list(self):
        self._pests_listbox.delete(0, tk.END)
        active_pests = [p for p in self._pests if p._active]
        if not active_pests:
            self._pests_listbox.insert(tk.END, "Нет активных вредителей")
        else:
            for pest in active_pests:
                self._pests_listbox.insert(tk.END, f"{pest._name} (шанс повреждения: {int(pest._damage_chance*100)}%)")

    def update_inventory_list(self):
        self._inventory_listbox.delete(0, tk.END)
        owned_poisons = [p for p in self._poisons if p._owned > 0]
        if not owned_poisons:
            self._inventory_listbox.insert(tk.END, "Нет средств для борьбы")
        else:
            for poison in owned_poisons:
                self._inventory_listbox.insert(tk.END, f"{poison._name}: {poison._owned} шт.")

    def update_info_label(self):
        self._info_label.config(text=f"День: {self._day} | Деньги: {self._money}₽ | Влажность: {self._humidity}% | Безопасность: {'★'*self._security_level}")

    def next_day(self):
        self._day += 1
        self._humidity = max(10, min(90, self._humidity + random.randint(-10, 10)))
        self.spawn_pests()

        damaged = []
        for pest in [p for p in self._pests if p._active]:
            for resource in self._resources:
                if pest.try_damage(resource):
                    damaged.append(resource._name)

        event_messages = []
        for event in self._random_events:
            if event.check_event(self):
                event._effect(self)
                event_messages.append(event._description)

        rent = sum(r._value * 0.1 for r in self._resources if not r._damaged)
        self._money += rent

        self.update_info_label()
        self.update_resources_list()
        self.update_pests_list()
        self.update_inventory_list()

        message = f"День {self._day} завершен.\nАрендная плата: +{rent:.1f}₽"
        if damaged:
            message += f"\nПовреждены: {', '.join(damaged)}"
        if event_messages:
            message += "\n\nСобытия:\n" + "\n".join(event_messages)

        messagebox.showinfo("Новый день", message)

        if all(not pest._active for pest in self._pests) and self._day > 10:
            messagebox.showinfo("Победа!", "Вы успешно управляли складом и уничтожили всех вредителей!")
            self._root.quit()

        if self._money < 0:
            messagebox.showinfo("Проигрыш", "У вас закончились деньги! Игра окончена.")
            self._root.quit()

    def spawn_pests(self):
        for pest in [p for p in self._pests if not p._active]:
            if pest.check_spawn_conditions(self):
                if 'humidity' in pest._spawn_conditions:
                    if self._humidity < pest._spawn_conditions['humidity']:
                        continue

                spawn_chance = 0.5
                if self._security_level > 1:
                    spawn_chance /= self._security_level

                if random.random() < spawn_chance:
                    pest._active = True

    def steal_resources(self, count):
        stealable = [r for r in self._resources if not r._damaged]
        if not stealable:
            return

        stolen = random.sample(stealable, min(count, len(stealable)))
        total_value = sum(r._value for r in stolen)

        success_chance = 0.7 / self._security_level
        if random.random() > success_chance:
            messagebox.showinfo("Кража предотвращена", "Охранник поймал вора!")
            return

        for r in stolen:
            self._resources.remove(r)

        self._money -= total_value * 0.5
        messagebox.showinfo("Кража", f"Украдено товаров на сумму {total_value}₽! Штраф: {total_value*0.5}₽")

    def fire_damage(self):
        for r in self._resources:
            if random.random() < 0.3:
                r._damaged = True

        for p in self._pests:
            if p._active and random.random() < 0.6:
                p._active = False

    def flood_damage(self):
        self._humidity = min(100, self._humidity + 20)

        for r in [res for res in self._resources if res._humidity_sensitive]:
            if random.random() < 0.5:
                r._damaged = True

        for p in [p for p in self._pests if p._name == "Плесень"]:
            if not p._active and random.random() < 0.7:
                p._active = True

    def add_money(self, amount):
        self._money += amount
        if amount >= 0:
            messagebox.showinfo("Удача", f"Вы получили {amount}₽")
        else:
            messagebox.showinfo("Неудача", f"Вы потеряли {-amount}₽")

    def buy_poison_menu(self):
        poison_window = tk.Toplevel(self._root)
        poison_window.title("Купить средство")
        poison_window.configure(bg='#B1E0F2')

        tk.Label(poison_window, text="Выберите средство для покупки:",
                font=('Arial', 12), bg='#B1E0F2').pack(pady=10)

        for poison in self._poisons:
            frame = tk.Frame(poison_window, bg='#B1E0F2')
            frame.pack(fill='x', padx=10, pady=5)

            btn_text = f"{poison._name} - {poison._cost}₽\nЭффективность: "
            btn_text += ", ".join([f"{k} {int(v*100)}%" for k, v in poison._effectiveness.items()])

            tk.Label(frame, text=btn_text, justify='left', bg='#B1E0F2').pack(side='left')

            def buy(p=poison):
                if self._money >= p._cost:
                    self._money -= p._cost
                    p._owned += 1
                    self.update_info_label()
                    self.update_inventory_list()
                    messagebox.showinfo("Успех", f"Вы купили {p._name}!")
                    poison_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Недостаточно денег!")

            tk.Button(frame, text="Купить", command=buy,
                     bg='#7FB3D5', activebackground='#5D8BF4', fg='white').pack(side='right')

    def use_poison_menu(self):
        active_pests = [p for p in self._pests if p._active]
        if not active_pests:
            messagebox.showinfo("Информация", "Нет активных вредителей!")
            return

        owned_poisons = [p for p in self._poisons if p._owned > 0]
        if not owned_poisons:
            messagebox.showinfo("Информация", "У вас нет средств для борьбы!")
            return

        poison_window = tk.Toplevel(self._root)
        poison_window.title("Использовать средство")
        poison_window.configure(bg='#B1E0F2')

        tk.Label(poison_window, text="Выберите средство для использования:",
                font=('Arial', 12), bg='#B1E0F2').pack(pady=10)

        for poison in owned_poisons:
            frame = tk.Frame(poison_window, bg='#B1E0F2')
            frame.pack(fill='x', padx=10, pady=5)

            btn_text = f"{poison._name} (осталось: {poison._owned})\nЭффективность: "
            btn_text += ", ".join([f"{k} {int(v*100)}%" for k, v in poison._effectiveness.items()])

            tk.Label(frame, text=btn_text, justify='left', bg='#B1E0F2').pack(side='left')

            def use(p=poison):
                killed = []
                for pest in active_pests:
                    if p.try_kill(pest):
                        pest._active = False
                        killed.append(pest._name)

                if killed:
                    message = f"Уничтожены: {', '.join(killed)}"
                else:
                    message = "Ни один вредитель не был уничтожен"

                self.update_pests_list()
                self.update_inventory_list()
                messagebox.showinfo("Результат", message)
                poison_window.destroy()

            tk.Button(frame, text="Использовать", command=use,
                     bg='#7FB3D5', activebackground='#5D8BF4', fg='white').pack(side='right')

    def repair_resources_menu(self):
        damaged = [r for r in self._resources if r._damaged]
        if not damaged:
            messagebox.showinfo("Информация", "Нет поврежденных ресурсов!")
            return

        cost_per_item = 25
        total_cost = len(damaged) * cost_per_item

        if self._money >= total_cost:
            self._money -= total_cost
            for r in damaged:
                r._damaged = False
            self.update_info_label()
            self.update_resources_list()
            messagebox.showinfo("Успех", f"Все ресурсы отремонтированы за {total_cost}₽")
        else:
            can_repair = self._money // cost_per_item
            if can_repair > 0:
                if messagebox.askyesno("Вопрос", f"У вас недостаточно денег для полного ремонта. Починить {can_repair} из {len(damaged)} за {can_repair*cost_per_item}₽?"):
                    self._money -= can_repair * cost_per_item
                    for r in random.sample(damaged, can_repair):
                        r._damaged = False
                    self.update_info_label()
                    self.update_resources_list()
                    messagebox.showinfo("Успех", f"Отремонтировано {can_repair} ресурсов")
            else:
                messagebox.showerror("Ошибка", f"Недостаточно денег! Нужно {total_cost}₽")

    def manage_warehouse(self):
        manage_window = tk.Toplevel(self._root)
        manage_window.title("Управление складом")
        manage_window.configure(bg='#B1E0F2')

        tk.Label(manage_window, text=f"Текущая влажность: {self._humidity}%",
                font=('Arial', 12), bg='#B1E0F2').pack(pady=5)

        def reduce_humidity():
            cost = 50
            if self._money >= cost:
                self._money -= cost
                self._humidity = max(10, self._humidity - 15)
                self.update_info_label()
                messagebox.showinfo("Успех", "Влажность уменьшена!")
                manage_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Недостаточно денег!")

        tk.Button(manage_window, text="Уменьшить влажность (-15%) - 50₽",
                 command=reduce_humidity, bg='#7FB3D5', activebackground='#5D8BF4', fg='white').pack(pady=5)

        tk.Label(manage_window, text=f"Текущий уровень безопасности: {'★'*self._security_level}",
                font=('Arial', 12), bg='#B1E0F2').pack(pady=5)

        if self._security_level < 3:
            def upgrade_security():
                cost = 300 * self._security_level
                if self._money >= cost:
                    self._money -= cost
                    self._security_level += 1
                    self.update_info_label()
                    messagebox.showinfo("Успех", "Безопасность улучшена!")
                    manage_window.destroy()
                else:
                    messagebox.showerror("Ошибка", "Недостаточно денег!")

            tk.Button(manage_window,
                     text=f"Улучшить безопасность (→{'★'*(self._security_level+1)}) - {300*self._security_level}₽",
                     command=upgrade_security, bg='#7FB3D5', activebackground='#5D8BF4', fg='white').pack(pady=5)
        else:
            tk.Label(manage_window, text="Достигнут максимальный уровень безопасности",
                    bg='#B1E0F2').pack(pady=5)

root = tk.Tk()
game = WarehouseGame(root)
root.mainloop()