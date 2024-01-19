from func import *
import sys

def main(args):
    np.set_printoptions(precision=7)
    if len(args) < 2: #Se não colocou nome do arquivo
        print("Coloque o nome do arquivo na linha de comando!")
        print("Ex.: python main.py nome_arquivo.txt")
        return

    arq_name = args[1]

    n, m, T, T_aux, B = ler_PL(arq_name) #Monta tableaux da PL original e auxiliar

    #Resolver auxiliar
    T_aux = colocar_canonica(T_aux, B, n)
    T_aux, B = resolve_auxiliar(T_aux, B, n)

    #Checa se é inviável
    if (T_aux[0,-1] < 0): #Se valor objetivo menor que 0
        print('inviavel')
        certificado_inviabilidade(T_aux,n)
        return

    #Resolver PL original
    if True in (B>=n+m+n): #Se a base possui variável exclusiva da PL auxiliar
        B = np.array(list(range(n+m,n+m+n))) #Torna base as variáveis de folga

    T = colocar_canonica(T, B, n) #Coloca em forma canônica

    j = achar_pivo(T, n)
    diagnostico = 'continua'
    while T[0,j] < 0: #Enquanto o elemento para pivoteamento for menor que 0
        T, B, diagnostico = passo(T, B, j) #Pivoteia

        if diagnostico == 'ilimitada': #Se detectou que é ilimitada
            break
        j = achar_pivo(T, n) #Acha próximo pivô

    if diagnostico == 'continua': #Se continuou até c < 0, achou ótimo
        _, col = T.shape
        print('otimo')
        print('{:.7f}'.format(T[0,col-1])) #Imprime valor ótimo
        solucao_otima(T, n, m, B) #Imprime solução
        certificado_otimalidade(T, n) #Imprime certificado
    else: #Se ilimitada
        print('ilimitada')
        solucao_ilimitada(T,n,m,B) #Imprime solução
        certificado_ilimitabilidade(T,B,j,m,n) #Imprime certificado

    return

main(sys.argv)