import netsquid as ns
import hashlib
import random

N = int(input("Please enter number of Bell states: N = "))
K0 =''.join([str(random.randint(0, 1)) for _ in range(2 * N)])
Ki = K0
print('K0 :', K0)
M = int(input("Please enter the communication times: M = "))

for i in range(1, M + 1):
    # mutual identity authentication
    rai = bin(random.randint(0, 1000))
    rbi = bin(random.randint(0, 1000))
    hash_object = hashlib.sha256(bytes(K0 + rai + rbi, 'utf-8'))
    hex_digs = hash_object.hexdigest()
    binary_result = bin(int(hex_digs, 16))[2:]
    if len(binary_result) > 2 * N:
        binary_result = binary_result[:2 * N]
    if len(binary_result) < 2 * N:
        binary_result = '0' * (2 * N - len(binary_result)) + binary_result
    K0A = binary_result
    K0B = binary_result
    print('K0A{} :'.format(i), K0A)
    print('K0B{} :'.format(i), K0B)

    def generate_single_photon(binary_string):
        # four single photons, a1=|0>, a2=|1>, a3=|+>, a4=|->
        a1, a2, a3, a4 = ns.qubits.create_qubits(4)
        ns.qubits.operate(a2, ns.X)
        ns.qubits.operate(a3, ns.H)
        ns.qubits.operate(a4, ns.X)
        ns.qubits.operate(a4, ns.H)
        QS = []  # store quantum states
        BS = []  # store measurement bases
        for i in range(0, len(binary_string)):
            if binary_string[i] == '0':
                QS.append(random.choice([a1, a2]))
                BS.append('Z')
            else:
                QS.append(random.choice([a3, a4]))
                BS.append('X')
        return QS, BS
    QS_Alice, BS_Alice = generate_single_photon(K0A)
    QS_Bob, BS_Bob = generate_single_photon(K0B)
    print('QS_Alice :', QS_Alice)
    # print('BS_Alice :', BS_Alice)
    print('QS_Bob :', QS_Bob)
    # print('BS_Bob :', BS_Bob)

    # measure QS_Alice and QS_Bob
    bell_operators = []
    p0, p1 = ns.Z.projectors
    bell_operators.append(ns.CNOT * (ns.H ^ ns.I) * (p0 ^ p0) * (ns.H ^ ns.I) * ns.CNOT)
    bell_operators.append(ns.CNOT * (ns.H ^ ns.I) * (p0 ^ p1) * (ns.H ^ ns.I) * ns.CNOT)
    bell_operators.append(ns.CNOT * (ns.H ^ ns.I) * (p1 ^ p0) * (ns.H ^ ns.I) * ns.CNOT)
    bell_operators.append(ns.CNOT * (ns.H ^ ns.I) * (p1 ^ p1) * (ns.H ^ ns.I) * ns.CNOT)
    def measure_single_photon(QS_Alice,QS_Bob):
        single_photon_results = []
        for j in range(0, 2*N):
            meas, prob = ns.qubits.gmeasure((QS_Alice[j], QS_Bob[j]), meas_operators=bell_operators)
            labels_bell = ("00", "01", "10", "11")
            single_photon_results.append(labels_bell[meas])
        return single_photon_results
    single_photon_measurement_results = measure_single_photon(QS_Alice, QS_Bob)
    # print(2 * N,'groups of single_photon_measurement_results :', single_photon_measurement_results)
    for j in range(0, 2 * N):
        Alice_Bell_Measurement = single_photon_measurement_results[0:N]
        Bob_Bell_Measurement = single_photon_measurement_results[N:2 * N]
        BS_Alice_1 = BS_Alice[0:N]
        BS_Alice_2 = BS_Alice[N:2 * N]
        BS_Bob_1 = BS_Bob[0:N]
        BS_Bob_2 = BS_Bob[N:2 * N]
    print('Alice gets the first', N, 'measurement results:', Alice_Bell_Measurement)
    print('Bob gets the last', N, 'measurement results :', Bob_Bell_Measurement)

    # randomly choose 00 or 11 (01 or 10)
    def random_choose(binary_string1, binary_string2, binary_string3):
        position = []
        if binary_string1 == '00' and binary_string2 == '11':
            for j in range(0, N):
                if binary_string3[j] == '00' or binary_string3[j] == '11':
                    position.append(str(j))
        else:
            for j in range(0, N):
                if binary_string3[j] == '10' or binary_string3[j] == '01':
                    position.append(str(j))
        return position

    # compare measurement bases
    def compare_bases(binary_string1, binary_string2, binary_string3):
        Error = 0
        for index in binary_string3:
            j = int(index)
            print('BS_Alice and BS_Bob :',binary_string1[j],binary_string2[j])
            if binary_string1[j] != binary_string2[j]:
                Error = Error + 1
        return Error

    Alice_random_choose = random_choose('00', '11', Alice_Bell_Measurement)
    print('Alice randomly chooses 00 or 11:', Alice_random_choose)
    print('BS_Alice_1:', BS_Alice_1,'BS_Bob_1:', BS_Bob_1)
    Alice_Error = compare_bases(BS_Alice_1, BS_Bob_1, Alice_random_choose)
    print('Alice compares the bases and computes the error rate :', Alice_Error/N)
    Bob_random_choose = random_choose('10', '01', Bob_Bell_Measurement)
    print('Bob randomly chooses 01 or 10:', Bob_random_choose)
    print('BS_Alice_2:', BS_Alice_2,'BS_Bob_2:', BS_Bob_2)
    Bob_Error = compare_bases(BS_Alice_2, BS_Bob_2, Bob_random_choose)
    print('Bob compares the bases and computes the error rate :', Bob_Error/N, '\n')

    # Encode Bell states
    def generates_bell_states(binary_string):
        bell_states = []  # store Bell state
        bell_states_1 = []  # store the first quantum state of Bell state
        bell_states_2 = []  # store the second quantum state of Bell state
        for i in range(0, len(binary_string), 2):
            if binary_string[i:i + 2] == '00':
                a1, a2 = ns.qubits.create_qubits(2)
                ns.qubits.operate(a1, ns.H)
                ns.qubits.operate([a1, a2], ns.CNOT)
                bell_states.append(ns.qubits.reduced_dm([a1, a2]))
                bell_states_1.append(a1)
                bell_states_2.append(a2)
            elif binary_string[i:i + 2] == '01':
                a1, a2 = ns.qubits.create_qubits(2)
                ns.qubits.operate(a2, ns.X)
                ns.qubits.operate(a1, ns.H)
                ns.qubits.operate([a1, a2], ns.CNOT)
                bell_states.append(ns.qubits.reduced_dm([a1, a2]))
                bell_states_1.append(a1)
                bell_states_2.append(a2)
            elif binary_string[i:i + 2] == '10':
                a1, a2 = ns.qubits.create_qubits(2)
                ns.qubits.operate(a1, ns.X)
                ns.qubits.operate(a1, ns.H)
                ns.qubits.operate([a1, a2], ns.CNOT)
                bell_states.append(ns.qubits.reduced_dm([a1, a2]))
                bell_states_1.append(a1)
                bell_states_2.append(a2)
            else:
                a1, a2 = ns.qubits.create_qubits(2)
                ns.qubits.operate(a1, ns.X)
                ns.qubits.operate(a2, ns.X)
                ns.qubits.operate(a1, ns.H)
                ns.qubits.operate([a1, a2], ns.CNOT)
                bell_states.append(ns.qubits.reduced_dm([a1, a2]))
                bell_states_1.append(a1)
                bell_states_2.append(a2)
        return bell_states, bell_states_1, bell_states_2
    TA0 = ''.join([str(random.randint(0, 1)) for _ in range(2 * N)])
    Bell_states_Alice, Bell_S1_Alice, Bell_S2_Alice = generates_bell_states(TA0)
    print('TA0 :', TA0)
    TB0 = ''.join([str(random.randint(0, 1)) for _ in range(2 * N)])
    Bell_states_Bob, Bell_S1_Bob, Bell_S2_Bob = generates_bell_states(TB0)
    print('TB0 :', TB0)

    # Encode Bell states
    def unitary_operations(binary_string1, binary_string2):
        bell_pauli = []  # store the Bell state after applying one Pauli operation
        operations = []  # store the Pauli operations
        img_number = complex(0, 1)
        for j in range(0, 2 * N, 2):
            if binary_string1[j:j + 2] == '00':
                ns.qubits.operate(binary_string2[int(j / 2)], ns.I)
                bell_pauli.append(binary_string2[int(j / 2)])
                operations.append('I')
            elif binary_string1[j:j + 2] == '01':
                ns.qubits.operate(binary_string2[int(j / 2)], ns.Z)
                bell_pauli.append(binary_string2[int(j / 2)])
                operations.append('Z')
            elif binary_string1[j:j + 2] == '10':
                ns.qubits.operate(binary_string2[int(j / 2)], ns.X)
                bell_pauli.append(binary_string2[int(j / 2)])
                operations.append('X')
            else:
                ns.qubits.operate(binary_string2[int(j / 2)], ns.Y)
                img_number * ns.qubits.reduced_dm(binary_string2[int(j / 2)])
                bell_pauli.append(binary_string2[int(j / 2)])
                operations.append('iY')
        return bell_pauli, operations
    KAi = ''.join([str(random.randint(0, 1)) for _ in range(2 * N)])
    Bell_S22_Bob_Alice, Alice_pauli_operations = unitary_operations(KAi, Bell_S2_Bob)
    print('KA{} :'.format(i), KAi)
    print('Alice_unitary_operations :', Alice_pauli_operations)
    KBi = ''.join([str(random.randint(0, 1)) for _ in range(2 * N)])
    Bell_S22_Alice_Bob, Bob_pauli_operations = unitary_operations(KBi, Bell_S2_Alice)
    print('KB{} :'.format(i), KBi)
    print('Bob_unitary_operations :', Bob_pauli_operations, '\n')

    # Measure Bell states
    def Alice_measure_bell_state(Bell_S1_Alice, Bell_S22_Alice_Bob):
        measurement_results = []  # store the Bell measurement results
        for j in range(0, N):
            meas, prob = ns.qubits.gmeasure((Bell_S1_Alice[j], Bell_S22_Alice_Bob[j]), meas_operators=bell_operators)
            labels_bell = ("00", "01", "10", "11")
            measurement_results.append(labels_bell[meas])
        return measurement_results
    TA = Alice_measure_bell_state(Bell_S1_Alice, Bell_S22_Alice_Bob)
    TA1 = ''.join(TA)
    print('TA1 :', TA1)

    def Bob_measure_bell_state(Bell_S1_Bob, Bell_S22_Bob_Alice):
        measurement_results = []  # store the Bell measurement results
        for j in range(len(Bell_S1_Alice)):
            meas, prob = ns.qubits.gmeasure((Bell_S1_Bob[j], Bell_S22_Bob_Alice[j]), meas_operators=bell_operators)
            labels_bell = ("00", "01", "10", "11")
            measurement_results.append(labels_bell[meas])
        return measurement_results
    TB = Bob_measure_bell_state(Bell_S1_Bob, Bell_S22_Bob_Alice)
    TB1 = ''.join(TB)
    print('TB1 :', TB1)

    # compare TA0 and TA1, TB0 and TB1
    def compare_types(binary_string1, binary_string2):
        key = []
        operations = []
        for j in range(0, 2 * N, 2):
            if binary_string1[j:j + 2] == '00':
                if binary_string2[j:j + 2] == '00':
                    key.append('00')
                    operations.append('I')
                elif binary_string2[j:j + 2] == '10':
                    key.append('01')
                    operations.append('Z')
                elif binary_string2[j:j + 2] == '01':
                    key.append('10')
                    operations.append('X')
                else:
                    key.append('11')
                    operations.append('iY')
            elif binary_string1[j:j + 2] == '01':
                if binary_string2[j:j + 2] == '01':
                    key.append('00')
                    operations.append('I')
                elif binary_string2[j:j + 2] == '11':
                    key.append('01')
                    operations.append('Z')
                elif binary_string2[j:j + 2] == '00':
                    key.append('10')
                    operations.append('X')
                else:
                    key.append('11')
                    operations.append('iY')
            elif binary_string1[j:j + 2] == '10':
                if binary_string2[j:j + 2] == '10':
                    key.append('00')
                    operations.append('I')
                elif binary_string2[j:j + 2] == '00':
                    key.append('01')
                    operations.append('Z')
                elif binary_string2[j:j + 2] == '11':
                    key.append('10')
                    operations.append('X')
                else:
                    key.append('11')
                    operations.append('iY')
            else:
                if binary_string2[j:j + 2] == '11':
                    key.append('00')
                    operations.append('I')
                elif binary_string2[j:j + 2] == '01':
                    key.append('01')
                    operations.append('Z')
                elif binary_string2[j:j + 2] == '10':
                    key.append('10')
                    operations.append('X')
                else:
                    key.append('11')
                    operations.append('iY')
        return key, operations
    K1, Bob_operations = compare_types(TA0, TA1)
    KBi = ''.join(K1)
    # print('Alice_gets_Bob_unitary_operation :', Bob_operations)
    print('Alice gets KB{} :'.format(i), KBi)
    K2, Alice_operations = compare_types(TB0, TB1)
    KAi = ''.join(K2)
    # print('Bob_gets_Alic_unitary_operation :', Alice_operations)
    print('Bob gets KA{} :'.format(i), KAi)

    # generate the secret key KAB and the authentication key Ki
    KABi = KAi + KBi
    Ki_next = ''
    for char_a, char_b, char_c in zip(Ki, KAi, KBi):
        xor_value = int(char_a) ^ int(char_b) ^ int(char_c)
        Ki_next += str(xor_value)
    Ki = Ki_next
    print('The secret key', 'KAB{} :'.format(i), KABi)
    print('The authentication key', f'K{i} :', Ki_next)
    print("Communication attempt", i, "out of", M, '\n')