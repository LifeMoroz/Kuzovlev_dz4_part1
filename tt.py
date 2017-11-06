import math

lambda_1 = 1 - 0.99999273916848708

import xlwt

font0 = xlwt.Font()
font0.name = 'Times New Roman'

style0 = xlwt.XFStyle()
style0.font = font0

font1 = xlwt.Font()
font1.name = 'Times New Roman'
font1.colour_index = 2
font1.bold = True

style1 = xlwt.XFStyle()
style1.font = font1

wb = xlwt.Workbook()

for disable_price in [500, 1500]:
    ws = wb.add_sheet('Disable price {}'.format(disable_price))
    INC = 0
    ws.write(INC, 0, "Количество ПК: ", style0)
    ws.write(INC, 1, "Интенсивность отказов:", style0)
    ws.write(INC, 2, "Время обслуживания:", style0)
    ws.write(INC, 3, "Стоимость часа:", style0)
    ws.write(INC, 4, "N", style0)
    ws.write(INC, 5, "Среднее число занятых каналов", style0)
    ws.write(INC, 6, "Среднее количество заявок в очереди", style0)
    ws.write(INC, 7, "Среднее время в очереди", style0)
    ws.write(INC, 8, "Будет затрачено на ремонт за год (часов)", style0)
    ws.write(INC, 9, "Простой за год (часов)", style0)
    ws.write(INC, 10, "Из них переработки", style0)
    ws.write(INC, 11, "Доплата за переработку", style0)
    ws.write(INC, 12, "Будет затрачено на ремонт за год (руб)", style0)
    ws.write(INC, 13, "Простой за год (руб)", style0)
    ws.write(INC, 14, "Суммарные потери", style0)
    INC = +1
    min_dict = {}
    for number in [10000, 100000]:
        min_cost = float('inf')

        def lam(pos=None):
            return number * lambda_1

        for nu, price in [(0.33, 30000), (1, 60000)]:
            for N in range(1, 10):

                def mu(pos):
                    if pos < N:
                        return (pos + 1) * nu
                    return nu*N


                po = lam() / nu

                if po/N >= 1:
                    print("Warning! Unstable for N =", N)
                    continue

                p0 = 1
                tmp = 1
                arr = []
                for i in range(number + 1):
                    tmp *= lam(i) / mu(i)
                    arr.append(tmp)
                    p0 += tmp

                p0 = 1 / p0


                def p(j):
                    return p0 * arr[j - 1]

                L = (po ** (N + 1)) * p0 / (N * math.factorial(N)) * ((1 - po/N) ** -2)
                Lsist = L + po
                hours_for_repair = lam() * 8776 * (Lsist / lam() - int(1/nu))
                repair_cost = N * price * 12
                additional_hours = hours_for_repair - N * 8 * 250
                if additional_hours > 0:
                    additional_repair_price = additional_hours * (price / 21 / 40) * 1.5
                    repair_cost += additional_repair_price
                cost_2 = hours_for_repair * disable_price
                cost_sum = repair_cost + cost_2
                if cost_sum < min_cost:
                    min_cost = cost_sum
                    min_dict[number] = ((nu, price), N, cost_sum)

                ws.write(INC, 0, number, style0)
                ws.write(INC, 1, lam(), style0)
                ws.write(INC, 2, int(1 / nu), style0)
                ws.write(INC, 3, price, style0)
                ws.write(INC, 4, N, style0)
                ws.write(INC, 5, po, style0)
                ws.write(INC, 6, Lsist, style0)
                ws.write(INC, 7, Lsist / lam(), style0)
                ws.write(INC, 8, lam() * 8776 * int(1 / nu), style0)
                ws.write(INC, 9, hours_for_repair, style0)
                ws.write(INC, 10, additional_hours, style0)
                ws.write(INC, 11, additional_hours * price * 1.5, style0)
                ws.write(INC, 12, repair_cost, style0)
                ws.write(INC, 13, cost_2, style0)
                ws.write(INC, 14, cost_sum, style0)
                INC += 1

    for number, value in min_dict.items():
        ws.write(INC, 0, "Количество компьютеров:", style1)
        ws.write(INC, 1, number, style1)
        ws.write(INC, 2, "Tобр:", style1)
        ws.write(INC, 3, int(1 / value[0][0]), style1)
        ws.write(INC, 4, "Цена одного мес.:", style1)
        ws.write(INC, 5, value[0][1], style1)
        ws.write(INC, 6, "ремонтников", style1)
        ws.write(INC, 7, value[1], style1)
        ws.write(INC, 8, "затраты", style1)
        ws.write(INC, 9, value[2], style1)
        INC += 1
        print("Количество компьютеров:", number)
        print("Tобр:", int(1/value[0][0]), "цена одного мес.:", value[0][1], "ремонтников:", value[1], "затраты", value[2])

wb.save('xl_rec.xls')
