# Вывод функций выходов и возбуждения RS

Вариант 5. Автомат Мура с состояниями S0–S6 и остановкой в S6 до синхронного RESET. Исходные данные — таблица аппаратной реализации из раздела 8.3.

## 1. Обозначения и исходные данные

F1, F2, F3 — входные сигналы; Y1–Y5 — выходные сигналы. Разряды текущего кода состояния обозначим α1, α2, α3:

$$\alpha_1=q_2,\qquad \alpha_2=q_1,\qquad \alpha_3=q_0.$$

В конъюнкции кода бит 1 записывается без отрицания, бит 0 — с отрицанием. Например, индикатор состояния S1 с кодом 001:

$$z_1=\overline{\alpha_1}\,\overline{\alpha_2}\alpha_3.$$

В общем случае zj=1 только в состоянии с кодом j. z7 соответствует неиспользуемому коду 111. Конъюнкция кода становится частью Yj, если этот выход активен в данном состоянии; все такие части объединяются через ИЛИ.

| Состояние | Код α1α2α3 | Y1Y2Y3Y4Y5 | Активные выходы |
| --- | --- | --- | --- |
| S0 | 000 | 00000 | — |
| S1 | 001 | 10101 | Y1, Y3, Y5 |
| S2 | 010 | 01010 | Y2, Y4 |
| S3 | 011 | 10010 | Y1, Y4 |
| S4 | 100 | 10001 | Y1, Y5 |
| S5 | 101 | 01101 | Y2, Y3, Y5 |
| S6 | 110 | 00000 | — |
| Неиспользуемый | 111 | 00000 | — |

Для входов триггеров используем обозначения с индексом разряда α, чтобы не смешивать их с именами состояний:

| Разряд памяти | Вход установки | Вход сброса | Имена в существующей схеме |
| --- | --- | --- | --- |
| α1=q2 | Sα1 | Rα1 | S2, R2 |
| α2=q1 | Sα2 | Rα2 | S1, R1 |
| α3=q0 | Sα3 | Rα3 | S0, R0 |

Выбор возбуждения RS принят тот же, что в аппаратной таблице:

| αi | αi после такта | Sαi | Rαi |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 0 | 1 |
| 1 | 1 | 0 | 0 |

При удержании используется пара 00. Далее сначала получаем функции при RESET=0; верхний индекс (0) у S/R обозначает именно этот режим.

<!-- pagebreak -->

## 2. Построение функций выходов Мура

Выходы зависят только от текущего кода α1α2α3. Входы F1–F3 в их выражения не входят.

### Выход Y1

Активен в S1, S3, S4. Объединяем коды 001, 011, 100:

$$Y_1=z_1\vee z_3\vee z_4=\overline{\alpha_1}\,\overline{\alpha_2}\alpha_3\vee\overline{\alpha_1}\alpha_2\alpha_3\vee\alpha_1\overline{\alpha_2}\,\overline{\alpha_3}.$$

$$=\overline{\alpha_1}\alpha_3(\overline{\alpha_2}\vee\alpha_2)\vee\alpha_1\overline{\alpha_2}\,\overline{\alpha_3}.$$

$$Y_1=\overline{\alpha_1}\alpha_3\vee\alpha_1\overline{\alpha_2}\,\overline{\alpha_3}.$$

### Выход Y2

Активен в S2, S5. Коды 010 и 101 различаются во всех трёх битах, поэтому их конъюнкции не склеиваются:

$$Y_2=z_2\vee z_5=\overline{\alpha_1}\alpha_2\overline{\alpha_3}\vee\alpha_1\overline{\alpha_2}\alpha_3.$$

### Выход Y3

Активен в S1, S5. Коды 001 и 101 различаются только разрядом α1:

$$Y_3=z_1\vee z_5=\overline{\alpha_1}\,\overline{\alpha_2}\alpha_3\vee\alpha_1\overline{\alpha_2}\alpha_3.$$

$$=\overline{\alpha_2}\alpha_3(\overline{\alpha_1}\vee\alpha_1),\qquad Y_3=\overline{\alpha_2}\alpha_3.$$

### Выход Y4

Активен в S2, S3. Коды 010 и 011 различаются только разрядом α3:

$$Y_4=z_2\vee z_3=\overline{\alpha_1}\alpha_2\overline{\alpha_3}\vee\overline{\alpha_1}\alpha_2\alpha_3.$$

$$=\overline{\alpha_1}\alpha_2(\overline{\alpha_3}\vee\alpha_3),\qquad Y_4=\overline{\alpha_1}\alpha_2.$$

### Выход Y5

Активен в S1, S4, S5. Сначала объединяем коды 100 и 101:

$$Y_5=z_1\vee z_4\vee z_5=\overline{\alpha_1}\,\overline{\alpha_2}\alpha_3\vee\alpha_1\overline{\alpha_2}\,\overline{\alpha_3}\vee\alpha_1\overline{\alpha_2}\alpha_3.$$

$$=\overline{\alpha_2}\bigl(\overline{\alpha_1}\alpha_3\vee\alpha_1(\overline{\alpha_3}\vee\alpha_3)\bigr)=\overline{\alpha_2}(\overline{\alpha_1}\alpha_3\vee\alpha_1).$$

$$Y_5=\overline{\alpha_2}(\alpha_1\vee\alpha_3).$$

Использованы тождества A∨¬A=1 и A∨¬AB=A∨B. В состоянии S0, в конце S6 и при коде 111 все полученные Y равны 0.

<!-- pagebreak -->

## 3. Функции установки RS при RESET=0

Для Sαi выбираем только переходы 0→1 разряда αi. Каждый член — конъюнкция кода начального состояния и условия перехода. Условия нескольких переходов из одного состояния объединяем через ИЛИ.

### Установка α1: Sα1 (на схеме S2)

Разряд α1 устанавливается при S2→S4, S2→S5 и S3→S4:

$$S_{\alpha_1}^{(0)}=z_2F_2(F_3\vee F_1)\vee z_2F_2\overline{F_3}\,\overline{F_1}\vee z_3.$$

Так как (F3∨F1)∨¬F3¬F1=1, получаем z2F2∨z3. Подставим коды:

$$=\overline{\alpha_1}\alpha_2\overline{\alpha_3}F_2\vee\overline{\alpha_1}\alpha_2\alpha_3=\overline{\alpha_1}\alpha_2(\overline{\alpha_3}F_2\vee\alpha_3).$$

$$S_{\alpha_1}^{(0)}=\overline{\alpha_1}\alpha_2(\alpha_3\vee F_2).$$

### Установка α2: Sα2 (на схеме S1)

Разряд α2 устанавливается при S1→S2, S5→S3 и S5→S6:

$$S_{\alpha_2}^{(0)}=z_1\vee z_5\overline{F_1}\,\overline{F_2}\vee z_5F_1=z_1\vee z_5(F_1\vee\overline{F_2}).$$

$$=\overline{\alpha_1}\,\overline{\alpha_2}\alpha_3\vee\alpha_1\overline{\alpha_2}\alpha_3(F_1\vee\overline{F_2}).$$

$$=\overline{\alpha_2}\alpha_3\bigl(\overline{\alpha_1}\vee\alpha_1(F_1\vee\overline{F_2})\bigr).$$

$$S_{\alpha_2}^{(0)}=\overline{\alpha_2}\alpha_3(\overline{\alpha_1}\vee F_1\vee\overline{F_2}).$$

### Установка α3: Sα3 (на схеме S0)

Разряд α3 устанавливается при S0→S1, S2→S3, S2→S5 и S4→S5:

$$S_{\alpha_3}^{(0)}=z_0\overline{F_2}\vee z_2\overline{F_2}\vee z_2F_2\overline{F_3}\,\overline{F_1}\vee z_4.$$

Для двух членов с z2 используем ¬F2∨F2B=¬F2∨B. Затем подставляем коды:

$$=\overline{\alpha_1}\,\overline{\alpha_2}\,\overline{\alpha_3}\,\overline{F_2}\vee\overline{\alpha_1}\alpha_2\overline{\alpha_3}(\overline{F_2}\vee\overline{F_1}\,\overline{F_3})\vee\alpha_1\overline{\alpha_2}\,\overline{\alpha_3}.$$

$$=\overline{\alpha_3}\bigl(\overline{\alpha_1}\,\overline{F_2}(\overline{\alpha_2}\vee\alpha_2)\vee\overline{\alpha_1}\alpha_2\overline{F_1}\,\overline{F_3}\vee\alpha_1\overline{\alpha_2}\bigr).$$

$$S_{\alpha_3}^{(0)}=\overline{\alpha_3}\bigl(\alpha_1\overline{\alpha_2}\vee\overline{\alpha_1}(\overline{F_2}\vee\alpha_2\overline{F_1}\,\overline{F_3})\bigr).$$

Это алгебраически упрощённые формы; глобальный минимум числа вентилей для всей схемы здесь не заявляется.

<!-- pagebreak -->

## 4. Функции сброса RS при RESET=0

Для Rαi выбираем только переходы 1→0 разряда αi. Переход неиспользуемого кода 111→000 добавляет член z7 во все три функции сброса.

### Сброс α1: Rα1 (на схеме R2)

Разряд α1 сбрасывается при S5→S3 и при восстановлении 111→000:

$$R_{\alpha_1}^{(0)}=z_5\overline{F_1}\,\overline{F_2}\vee z_7=\alpha_1\overline{\alpha_2}\alpha_3\overline{F_1}\,\overline{F_2}\vee\alpha_1\alpha_2\alpha_3.$$

$$=\alpha_1\alpha_3(\overline{\alpha_2}\,\overline{F_1}\,\overline{F_2}\vee\alpha_2).$$

$$R_{\alpha_1}^{(0)}=\alpha_1\alpha_3(\alpha_2\vee\overline{F_1}\,\overline{F_2}).$$

### Сброс α2: Rα2 (на схеме R1)

Разряд α2 сбрасывается при S2→S4, S2→S5, S3→S4 и 111→000. Как при выводе Sα1, два условия из S2 объединяются в F2:

$$R_{\alpha_2}^{(0)}=z_2F_2(F_3\vee F_1)\vee z_2F_2\overline{F_3}\,\overline{F_1}\vee z_3\vee z_7=z_2F_2\vee z_3\vee z_7.$$

$$=\overline{\alpha_1}\alpha_2\overline{\alpha_3}F_2\vee\overline{\alpha_1}\alpha_2\alpha_3\vee\alpha_1\alpha_2\alpha_3.$$

$$=\alpha_2(\overline{\alpha_1}\,\overline{\alpha_3}F_2\vee\alpha_3),\qquad R_{\alpha_2}^{(0)}=\alpha_2(\alpha_3\vee\overline{\alpha_1}F_2).$$

### Сброс α3: Rα3 (на схеме R0)

Разряд α3 сбрасывается при S1→S2, S3→S4, S5→S4, S5→S6 и 111→000:

$$R_{\alpha_3}^{(0)}=z_1\vee z_3\vee z_5\overline{F_1}F_2F_3\vee z_5F_1\vee z_7.$$

$$=z_1\vee z_3\vee z_5(F_1\vee F_2F_3)\vee z_7.$$

$$=\overline{\alpha_1}\,\overline{\alpha_2}\alpha_3\vee\overline{\alpha_1}\alpha_2\alpha_3\vee\alpha_1\overline{\alpha_2}\alpha_3(F_1\vee F_2F_3)\vee\alpha_1\alpha_2\alpha_3.$$

$$=\alpha_3\bigl(\overline{\alpha_1}\vee\alpha_1\overline{\alpha_2}(F_1\vee F_2F_3)\vee\alpha_1\alpha_2\bigr).$$

Последовательно применяем ¬A∨AB=¬A∨B и A∨¬AB=A∨B:

$$R_{\alpha_3}^{(0)}=\alpha_3(\overline{\alpha_1}\vee\alpha_2\vee F_1\vee F_2F_3).$$

Слагаемое перехода S5→S4 сохранено для формального набора F=011. Недостижимые при реальных F(X) сочетания не использованы как неопределённые значения.

<!-- pagebreak -->

## 5. Учёт RESET и проверка решения

Обозначим ρ=RESET. Это общий синхронный сброс, отличный от входов R отдельных триггеров. Для каждого i=1,2,3:

$$S_{\alpha_i}=\overline{\rho}\,S_{\alpha_i}^{(0)},\qquad R_{\alpha_i}=\rho\alpha_i\vee R_{\alpha_i}^{(0)}.$$

При ρ=0 получаем выведенные функции. При ρ=1 все S равны 0, а Rαi=αi, поэтому на ближайшем фронте CLK код станет 000.

### Почему запрещённое сочетание не возникает

В каждой функции установки есть множитель ¬αi, а в каждой функции сброса — αi. Поэтому и с учётом RESET:

$$S_{\alpha_i}R_{\alpha_i}=0,\qquad \overline{\alpha_i}\alpha_i=0.$$

Характеристическое уравнение RS-триггера:

$$\alpha_i^{+}=S_{\alpha_i}\vee(\alpha_i\overline{R_{\alpha_i}}).$$

Оно даёт установку при SR=10, сброс при SR=01 и удержание при SR=00. Выходы Y после фронта рассчитываются уже по новому коду.

### Пример подстановки: S2→S4

Пусть текущее состояние S2, код 010; F1F2F3=111; RESET=0. Тогда α1=0, α2=1, α3=0. Из шести полученных функций:

$$S_{\alpha_1}=1,\quad S_{\alpha_2}=0,\quad S_{\alpha_3}=0.$$

$$R_{\alpha_1}=0,\quad R_{\alpha_2}=1,\quad R_{\alpha_3}=0.$$

Первый бит устанавливается, второй сбрасывается, третий удерживается:

$$\alpha_1^{+}\alpha_2^{+}\alpha_3^{+}=100,\qquad S2\longrightarrow S4.$$

До фронта активны Y2,Y4 (маска 01010), после фронта — Y1,Y5 (маска 10001). Это соответствует таблице переходов и выходам автомата Мура.

### Граничные случаи и исчерпывающая проверка

В S6 (110) при RESET=0 все S/R равны 0, поэтому конец удерживается. При неиспользуемом коде 111 все S равны 0, все R равны 1: за один фронт происходит восстановление в S0.

Пять функций Y проверены на всех 8 кодах. Все шесть функций S/R проверены на 8 кодах × 8 формальных наборах F × 2 значениях RESET, всего 128 случаях. Они совпадают с независимым интерпретатором исходного алгоритма и входами существующей вентильной схемы. Все 14 автоматических тестов прошли.

Итоговые формулы вычисляются отдельно в [ulu/derived.py](../ulu/derived.py); полный аппаратный синтез и схемы находятся в [разделе 8](08_hardware.md). Версия решения для печати: [PDF](../output/pdf/ALM_variant5_output_rs_derivation.pdf).
