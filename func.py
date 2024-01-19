import numpy as np

def montar_tableaux(n, m, c, A, b): #Monta tableaux da PL original
    novo_m = m + n #Variáveis + Variáveis de folga
    c = np.append(-c, np.zeros(n)) #Cria função objetiva com variáveis de folga
    
    T = np.zeros((1+n, n+novo_m+1)) #Cria tableaux = 0
    
    vero = np.zeros(n) #Primeira linha de VERO
    T[0] = np.append(vero, np.append(c, [0])) #Primeira linha do tableaux
    for i in range(n): #Para cada linha/restrição
        vero = np.zeros(n)
        vero[i] = 1 # i-ésima linha do VERO
        T[i+1] = np.append(vero, np.append(A[i,:], np.append(vero, [b[i]]))) #i-ésima linha do tableaux

    return T

def montar_auxiliar(n, m, T): #Monta tableaux da PL auxiliar
    linhas = n+1
    colunas = n+m+n+n+1 #Mais n variáveis (auxiliares)
    T_aux = np.zeros((linhas,colunas)) #Cria tableaux auxiliar = 0
    T_aux[0] = np.append(np.zeros(n+m+n), np.append(np.ones(n), T[0,-1])) #Primeira linha, só variáveis auxiliares são 1, resto 0
    
    for i in range(1, n+1): #Para as outras linhas
        valores = np.zeros(n)
        valores[i-1] = 1 #Matriz abaixo das variáveis novas é identidade
        if T[i,-1] < 0:
            T[i,:] *= -1 #Multiplica linha de T por -1 se b < 0

        T_aux[i,:] = np.append(T[i,:-1], np.append(valores, T[i,-1])) #Coloca matriz identidade entre A e b

    B = np.array(list(range(n+m+n, n+m+n+n))) #Base inicial são as variáveis novas

    return T_aux, B

def ler_PL(arq_name): #Processa a PL
    with open(arq_name) as arq:
        n, m = [int(x) for x in next(arq).split()] # Lê a primeira linha
        c = np.array([float(x) for x in next(arq).split()]) # Lê a segunda linha (função objetiva)
        A = np.zeros((n, m)) #Inicializa A = 0
        b = np.zeros((n,1)) #Inicializa b = 0
        i = 0
        for linha in arq: # Lê resto das linhas (restrições)
            restricao = [float(x) for x in linha.split()] #Separa os números da linhas
            A[i] = restricao[:m] #m primeiros são a linha i de A
            b[i] = restricao[m] #último é elemento i de b
            i += 1

    T = montar_tableaux(n, m, c, A, b) #Monta tableaux da PL original
    T_aux, B = montar_auxiliar(n, m, T) #Monta tableaux da PL auxiliar
    return n, m, T, T_aux, B

def colocar_canonica(T, B, n): #Coloca tableaux em forma canônica
    for i in range(len(B)): #Variáveis na base
        j = B[i]
        T[i+1,:] /= T[i+1,j] #Torna elemento escolhido 1
        for k in range(n+1): #Para todas as linhas
            if k != i+1 and T[i+1,j] != 0: #Menos a própria
                mult = T[k,j]/T[i+1,j] #Zera a linha
                T[k,:] -= mult*T[i+1,:]
    return T

def passo(T, B, j): #Pivoteia uma coluna
    linhas, colunas = T.shape

    razao_min = -1
    i_min = -1
    for i in range(1,linhas): #Para todas as restrições
        if T[i,j] != 0: #Para evitar divisões por 0
            razao = T[i,colunas-1] / T[i,j]
            if razao >= 0: #Se x < razao, razao precisa ser >= 0
                if razao_min == -1 or razao_min > razao:
                    razao_min = razao
                    i_min = i
    
    if i_min == -1: #Se i_min = -1 é ilimitada (A[j] <= 0)
        return T, B, 'ilimitada'
    
    T[i_min,:] /= T[i_min,j] #Se não detectou ilimitada, coloca em formato canonico, elemento vira 1
    for i in range(linhas): #Zera outras linhas do Tableaux
        if i != i_min:
            mult = T[i,j]/T[i_min,j]
            T[i,:] -= mult*T[i_min,:]
    B[i_min-1] = j #Coloca elemento na posição do array de base de acordo com a posição da coluna na matriz identidade 
                   #(ex.: coluna 0 1 0 em segunda posição)

    return T, B, 'continua'
    
def achar_pivo(T,n): #Acha próxima coluna a ser pivoteada
    j = np.where(T[0,:] == np.min(T[0,n:-1])) #Pega menor elemento dos que podem ser pivoteados
    
    for k in j[0]:
        if k >= n:
            j_n = k
            break

    return j_n

def resolve_auxiliar(T, B, n): #Resolve auxiliar
    x,_ = T.shape
    j = achar_pivo(T,n) #Acha pivô
    while T[0,j] < 0 and j > n-1: #Se j não está no VERO e é >= 0
        T, B, _ = passo(T, B, j) #Pivoteia na coluna j

        j = achar_pivo(T,n) #Acha novo pivô

    return T,B

def certificado_inviabilidade(T,n): #Imprime certificado de inviabilidade
    certificado = ''
    for i in range(n):
        certificado += '{:.7f} '.format(T[0, i]) #Lista elementos da primeira linha do VERO com 7 casas decimais
    print(certificado[:-1])

def solucao_otima(T, n, m, B): #Imprime solução ótima
    B -= n #Retira índices do VERO para comparar com variáveis
    solucao = ''
    
    for i in range(m): #Para toda variável (excluindo as de folga e auxiliares)
        if i in B: #Se é básica
            j = np.where(B == i)[0][0] #Posição em B indica qual coluna da matriz identidade é
            solucao += '{:.7f} '.format(T[j+1, -1]) #Adiciona o valor de b correspondente
        else: #Se não é básica
            solucao += '{:.7f} '.format(0.0) #Adiciona 0
    print(solucao[:-1])

def certificado_otimalidade(T, n): #Imprime certificado de otimalidade
    certificado = ''
    for i in range(n):
        certificado += '{:.7f} '.format(T[0, i]) #Lista elementos da primeira linha do VERO com 7 casas decimais
    print(certificado[:-1])

def solucao_ilimitada(T, n, m, B): #Imprime uma solução viável para PL ilimitada
    B -= n #Retira índices do VERO para comparar com variáveis
    solucao = ''
    
    for i in range(m): #Para toda variável (excluindo as de folga e auxiliares)
        if i in B: #Se é básica
            j = np.where(B == i)[0][0] #Posição em B indica qual coluna da matriz identidade é
            solucao += '{:.7f} '.format(T[j+1, -1]) #Adiciona o valor de b correspondente
        else: #Se não é básica
            solucao += '{:.7f} '.format(0.0) #Adiciona 0
    print(solucao[:-1])

def certificado_ilimitabilidade(T, B, j, m, n): #Imprime certificado de ilimitabilidade
    certificado = ''
    for variavel in range(m): #Para toda variável
        if variavel in B: #Se está na base
            posicao = np.where(B == variavel)[0][0]
            certificado += '{:.7f} '.format(-T[posicao+1,j]) #Valor no certificado é oposto da entrada da problemática em sua posição na base
        elif variavel == j-n: #Se é a problemática
            certificado += '{:.7f} '.format(1.0) #Valor no certificado é 1
        else: #Não é básica ou problemática
            certificado += '{:.7f} '.format(0.0) #Valor no certificado é 0
    print(certificado[:-1])