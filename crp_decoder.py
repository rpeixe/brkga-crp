from crp_instance import CrpInstance
import math
from brkga_mp_ipr.types import BaseChromosome

class CrpDecoder():
    """
    Simple Traveling Salesman Problem decoder. It creates a permutation of
    nodes induced by the chromosome and computes the cost of the tour.
    """

    def __init__(self, instance: CrpInstance):
        self.instance = instance

    ###########################################################################

    def decode(self, chromosome: BaseChromosome, rewrite: bool) -> float:
        def get_cultura_normal(valor):
          "Retorna o indice da cultura na matriz dado o valor do índice no cromossomo"
          for i in range(len(self.instance.posicao_cultura)):
            if valor<self.instance.posicao_cultura[i]:
              return i

        def planta(cultura,lote,tempo):
          for i in range(self.instance.matriz_dados[cultura][2]):
            self.instance.terrenos[lote][enforce_borders(tempo+i)] = cultura
          return enforce_borders(tempo + self.instance.matriz_dados[cultura][2])

        def get_family(lote, tempo):
          "Retorna a familia da cultura em dado lote e tempo"
          if self.instance.terrenos[lote][tempo] == -1:
            return -1
          else:
            return self.instance.matriz_dados[self.instance.terrenos[lote][tempo]][1]
          
        def enforce_borders(tempo):
          dp = self.instance.duracao_plantio
          if tempo < 0:
            return tempo + dp
          else:
            return tempo % dp

        def viabilidade(cultura,lote,tempo):
          "Retorna se é possível plantar a cultura no lote e tempo especificados"

          # print("Cultura: " + str(cultura) + " Lote: " + str(lote) + " Tempo: " + str(tempo))

          duracao_cultura = self.instance.matriz_dados[cultura][2]

          # Já tem cultura da mesma família antes ou depois
          if self.instance.matriz_dados[cultura][1] == get_family(lote, enforce_borders(tempo + duracao_cultura + 1)):
              return False
          elif self.instance.matriz_dados[cultura][1] == get_family(lote, enforce_borders(tempo - duracao_cultura - 1)):
              return False

          for i in range(self.instance.matriz_dados[cultura][2]):
            # Já tem algo plantado
            if self.instance.terrenos[lote][enforce_borders(tempo+i)] != -1:
              return False
            # Já tem cultura da mesma família no lote adjacente
            elif lote>0 and get_family(lote-1, enforce_borders(tempo+i)) == self.instance.matriz_dados[cultura][1]:
              return False

          return True

        def denormalize(float_number, max):
          "Retorna um inteiro de 0 a max-1"
          return math.ceil(float_number * max) - 1

        def calcula_custo():
          "Calcula o custo total da solução"
          custo = 0
          for i in range(self.instance.numero_lotes):
            tempo_para_pousio = False
            nada_seguido = 0
            for j in range(self.instance.duracao_plantio):
              if self.instance.terrenos[i][j] == -1:
                custo += 1
                nada_seguido += 1
                if nada_seguido >= 3:
                  tempo_para_pousio = True
              else:
                nada_seguido = 0
            if not tempo_para_pousio:
              custo += 999999999 # inviavel
          return custo

        self.instance.reset()
        permutation = sorted((key, index) for index, key in enumerate(chromosome[:self.instance.vetor_culturas_tam]))
        lista_culturas = list(get_cultura_normal(value) for index, value in permutation)

        # print("Permutação")
        # print(permutation)
        # print("Posicao cultura")
        # print(self.instance.posicao_cultura)
        # print("Lista de culturas")
        # print(lista_culturas)

        for i in range(self.instance.numero_lotes):
          verdinha = self.instance.cultura_normal + denormalize(chromosome[self.instance.vetor_culturas_tam+(2*i)], self.instance.cultura_verde)
          posicao_verdinha_ini = denormalize(chromosome[self.instance.vetor_culturas_tam+(2*i)+1],self.instance.duracao_plantio)
          posicao_verdinha = posicao_verdinha_ini

          # print("Lista de culturas")
          # print(lista_culturas)

          # Tenta plantar a verdinha
          while(not viabilidade(verdinha,i,posicao_verdinha)):
            posicao_verdinha = (posicao_verdinha + 1) % self.instance.duracao_plantio
            if posicao_verdinha == posicao_verdinha_ini:
              return 99999999999 # deu merda
          else:
            next_position = planta(verdinha,i,posicao_verdinha) # deu bom

          # Tenta plantar as outras culturas na ordem
          nova_lista_culturas = []
          for j in range(len(lista_culturas)):
            cultura = lista_culturas[j]
            if viabilidade(cultura, i, next_position):
              next_position = planta(cultura, i, next_position)
              if self.instance.terrenos[i][enforce_borders(next_position + self.instance.min_duracao)] != -1:
                nova_lista_culturas.extend(lista_culturas[j+1:])
                break # ja esta cheio
            else:
              nova_lista_culturas.append(cultura)
          lista_culturas = nova_lista_culturas

        return calcula_custo()
