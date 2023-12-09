import matplotlib.pyplot as plt
import math
from crp_instance import CrpInstance
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
        self.build_terrain(chromosome)

        return self.calcula_custo()

    ###########################################################################
    def build_terrain(self, chromosome):
      self.instance.reset()
      permutation = sorted((key, index) for index, key in enumerate(chromosome[:self.instance.vetor_culturas_tam]))
      lista_culturas = list(self.get_cultura(value) for index, value in permutation)

      for i in range(self.instance.numero_lotes):
        tempo_ini = self.denormalize(chromosome[self.instance.vetor_culturas_tam + i],self.instance.duracao_plantio)

        next_position = self.planta(self.instance.cultura_pousio, i, tempo_ini)

        # Tenta plantar as outras culturas na ordem
        nova_lista_culturas = []
        cultura_verde_plantada = False
        for j in range(len(lista_culturas)):
          cultura_atual = lista_culturas[j]
          if cultura_atual >= self.instance.num_culturas_normais and cultura_atual != self.instance.cultura_pousio:
            # Cultura verde
            cultura_atual = self.instance.cultura_verde
            if cultura_verde_plantada:
              nova_lista_culturas.append(cultura_atual)
              continue

          if self.viabilidade(cultura_atual, i, next_position):
            next_position = self.planta(cultura_atual, i, next_position)
            if cultura_atual >= self.instance.num_culturas_normais and cultura_atual != self.instance.cultura_pousio:
              # Cultura verde
              cultura_verde_plantada = True

            if self.instance.terrenos[i][self.wrap(next_position + self.instance.min_duracao)] != -1:
              nova_lista_culturas.extend(lista_culturas[j+1:])
              break # ja esta cheio
          else:
            nova_lista_culturas.append(cultura_atual)

        lista_culturas = nova_lista_culturas
      for i in range(self.instance.numero_lotes):
        # Segunda passada
        custo1 = self.calcula_custo_lote(i)
        if custo1 > 0:
          lote_antigo = list(self.instance.terrenos[i])
          lista_culturas_antiga = list(lista_culturas)
          for j in range(self.instance.duracao_plantio):
            if self.instance.terrenos[i][j] != -1 and self.instance.terrenos[i][j] != self.instance.cultura_pousio and self.instance.terrenos[i][j] != self.instance.terrenos[i][self.wrap(j-1)]:
              lista_culturas.append(self.instance.terrenos[i][j])
              self.desplanta(i, j)
          tempo_ini = self.denormalize(chromosome[self.instance.vetor_culturas_tam + i],self.instance.duracao_plantio)

          next_position = self.wrap(tempo_ini + self.instance.duracao_pousio)

          # Tenta plantar as outras culturas na ordem
          nova_lista_culturas = []
          cultura_verde_plantada = False
          for j in range(len(lista_culturas)):
            cultura_atual = lista_culturas[j]
            if cultura_atual >= self.instance.num_culturas_normais and cultura_atual != self.instance.cultura_pousio:
              # Cultura verde
              cultura_atual = self.instance.cultura_verde
              if cultura_verde_plantada:
                nova_lista_culturas.append(cultura_atual)
                continue

            if self.viabilidade(cultura_atual, i, next_position):
              next_position = self.planta(cultura_atual, i, next_position)
              if cultura_atual >= self.instance.num_culturas_normais and cultura_atual != self.instance.cultura_pousio:
                # Cultura verde
                cultura_verde_plantada = True

              if self.instance.terrenos[i][self.wrap(next_position + self.instance.min_duracao)] != -1:
                nova_lista_culturas.extend(lista_culturas[j+1:])
                break # ja esta cheio
            else:
              nova_lista_culturas.append(cultura_atual)
          custo2 = self.calcula_custo_lote(i)
          if custo2 < custo1:
            lista_culturas = nova_lista_culturas
          else:
            lista_culturas = lista_culturas_antiga
            self.instance.terrenos[i] = lote_antigo

    
    def draw_chart(self, chromosome):
      def get_bar_length(lote, tempo):
        cultura = self.instance.terrenos[lote][tempo]
        length = 0
        i = tempo
        while  i < self.instance.duracao_plantio and self.instance.terrenos[lote][i] == cultura:
          length += 1
          i += 1
        return length

      self.build_terrain(chromosome)
      fig, ax = plt.subplots()

      for i in range(self.instance.numero_lotes):
        cultura_atual = None
        for j in range(self.instance.duracao_plantio):
          if self.instance.terrenos[i][j] != cultura_atual:
            cultura_atual = self.instance.terrenos[i][j]
            length = get_bar_length(i, j)
            ax.broken_barh([(j, length)], (i+0.5, 1), facecolor='white', edgecolor='black')
            ax.text(j + length/2, i+1, str(cultura_atual+1), va = 'center', ha = 'center', size = 'small')
      ax.set_ylim(0.5, self.instance.numero_lotes + 0.5)
      ax.set_xlim(0, self.instance.duracao_plantio)
      ax.set_yticks([k for k in range(1, self.instance.numero_lotes+1)])
      ax.set_xticks([k for k in range(0, self.instance.duracao_plantio, 10)])

      plt.savefig("result.png")


    def get_cultura(self, valor):
      "Retorna o indice da cultura na matriz dado o valor do índice no cromossomo"
      for i in range(len(self.instance.posicao_cultura)):
        if valor<self.instance.posicao_cultura[i]:
          return i

    def planta(self, cultura,lote,tempo):
      "Planta a cultura começando no tempo indicado"
      if cultura != self.instance.cultura_pousio:
        duracao = self.instance.matriz_dados[cultura][2]
      else:
        duracao = self.instance.duracao_pousio
      for i in range(duracao):
        self.instance.terrenos[lote][self.wrap(tempo+i)] = cultura
      return self.wrap(tempo + duracao)
    
    def desplanta(self, lote,tempo):
      "Remove a cultura começando no tempo indicado"
      cultura = self.instance.terrenos[lote][tempo]

      if cultura != self.instance.cultura_pousio:
        duracao = self.instance.matriz_dados[cultura][2]
      else:
        duracao = self.instance.duracao_pousio
      for i in range(duracao):
        self.instance.terrenos[lote][self.wrap(tempo+i)] = -1

    def get_family(self, lote, tempo):
      "Retorna a familia da cultura em dado lote e tempo"
      if self.instance.terrenos[lote][tempo] == -1 or self.instance.terrenos[lote][tempo] == self.instance.cultura_pousio:
        return -1
      else:
        return self.instance.matriz_dados[self.instance.terrenos[lote][tempo]][1]
      
    def wrap(self, tempo):
      if tempo < 0:
        return tempo + self.instance.duracao_plantio
      else:
        return tempo % self.instance.duracao_plantio

    def viabilidade(self, cultura,lote,tempo):
      "Retorna se é possível plantar a cultura no lote e tempo especificados"

      duracao_cultura = self.instance.matriz_dados[cultura][2]

      # Já tem cultura da mesma família antes ou depois
      if self.instance.matriz_dados[cultura][1] == self.get_family(lote, self.wrap(tempo + duracao_cultura + 1)):
          return False
      elif self.instance.matriz_dados[cultura][1] == self.get_family(lote, self.wrap(tempo - 1)):
          return False

      for i in range(self.instance.matriz_dados[cultura][2]):
        # Já tem algo plantado
        if self.instance.terrenos[lote][self.wrap(tempo+i)] != -1:
          return False
        # Já tem cultura da mesma família no lote anterior
        elif lote > 0 and self.get_family(lote-1, self.wrap(tempo+i)) == self.instance.matriz_dados[cultura][1]:
          return False

      return True

    def denormalize(self, float_number, max):
      "Retorna um inteiro de 0 a max-1"
      return math.ceil(float_number * max) - 1

    def calcula_custo(self):
      "Calcula o custo total da solução"
      custo = 0

      for i in range(self.instance.numero_lotes):
        cv = 0
        for j in range(self.instance.duracao_plantio):
          cultura_terreno = self.instance.terrenos[i][j]
          #if cultura_terreno == -1 or (cultura_terreno >= self.instance.num_culturas_normais and cultura_terreno != self.instance.cultura_pousio):
          if cultura_terreno == -1:
            custo += 1
          if cultura_terreno != self.instance.cultura_pousio and cultura_terreno >= self.instance.num_culturas_normais and cultura_terreno != self.instance.terrenos[i][self.wrap(j+1)]:
            cv += 1
        if cv != 1:
          custo += 999999999
      return custo
    
    def calcula_custo_lote(self, lote):
      "Calcula o custo de um lote"
      custo = 0

      cv = 0
      for j in range(self.instance.duracao_plantio):
        cultura_terreno = self.instance.terrenos[lote][j]
        #if cultura_terreno == -1 or (cultura_terreno >= self.instance.num_culturas_normais and cultura_terreno != self.instance.cultura_pousio):
        if cultura_terreno == -1:
          custo += 1
        if cultura_terreno != self.instance.cultura_pousio and cultura_terreno >= self.instance.num_culturas_normais and cultura_terreno != self.instance.terrenos[lote][self.wrap(j+1)]:
          cv += 1
      if cv != 1:
        custo += 999999999
      return custo
