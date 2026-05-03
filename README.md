# Virtual Camera 3D

Nesse projeto, o objetivo é implementar uma Câmera 3D, tomando como base um modelo de uma câmara escura (pinhole camera) e seguindo o livro *Computer Graphics, Theory and Practice* de *Jonas Gomes e Luiz Velho*. Para instalação, veja o arquivo `setup.md`.

## 1 - Definições

Começaremos com definições e explicações importantes para o projeto. Nosso cenário é:

- Existe um **espaço do mundo**, que é o espaço da nossa simulação do que seria o mundo real, representando o espaço em que os objetos são posicionados e orientados, com seu respectivo sistema de coordenadas. Modelaremos uma quarta dimensão auxiliar, usada para tornar possível operações de translação serem multiplicações de matriz ao mesmo tempo em que criamos uma dimensão nova que pode guardar informações que serão úteis posteriormente.

- Para cada objeto do mundo, vamos considerar um **espaço do objeto**, que é um sistema de coordenadas definido de acordo com a geometria do objeto e orientado em referencial a ele.

- No sistema de coordenadas do mundo, existe um ponto $C$ chamado de **centro de projeção**, que é o local que representa onde a câmera deve estar enxergando. Também há um vetor $N$ chamado de **vetor do eixo ótico**, indicando a direção onde a câmera deve estar olhando. A reta definida por esse vetor é o **eixo ótico**. Nesse contexto, geralmente normalizamos esse vetor tomando $N' = \frac{N}{||N||}$, sendo o **vetor normal do eixo ótico**, pertencendo ao sistema de referência da câmera.

- Além disso, há uma distância $d$ do centro de projeção e perpendicular ao vetor $N$, há um plano retangular chamado de **plano de projeção**, onde $d$ é a **distância focal** da câmera.

- Também definimos um vetor $V$, o **vetor de inclinação** da câmera. O plano dos vetores $N$ e $V$ é o **plano vertical longitudinal** da câmera, onde rotacionar esse plano ao redor do eixo ótico nos dá a noção de inclinação da câmera em relação ao espaço do mundo.

- Para definir precisamente o sistema de coordenadas da câmera, precisamos de uma base ortonormal. Já temos o centro $C$ e o vetor normal do eixo ótico $N'$. Em seguida, definimos o **vetor vertical** da câmera como $v=\frac{V-\langle V,N' \rangle N'}{||V-\langle V,N' \rangle N'||}$. Também obtemos o **vetor lateral** da câmera (representando a direita) com $u = N' \times v$. O conjunto $(C,\{u,v,N'\})$ define o **espaço da câmera virtual**.

- O ponto onde o eixo ótico fura o plano de projeção é chamado de **ponto principal**. Usando esse ponto e os vetores $u$ e $v$, estabelece-se um sistema de coordenadas no plano de projeção, chamado de espaço da imagem. Dentro desse plano, delimitamos uma janela retangular chamada **tela virtual**, especificada pelos seus cantos $(u_{min}, v_{min})$ e $(u_{max}, v_{max})$. Ela atua como um molde da imagem final.

- O conjunto de semi-retas que partem do centro de projeção $C$ e passam pelas bordas da tela virtual forma uma pirâmide de base retangular no espaço, a **pirâmide de visão**. O raio que sai de $C$ e passa exatamente pelo centro da tela virtual é chamado de **eixo de visão**, que pode ser oblíquo e não coincidir com o eixo ótico, caso a tela virtual seja descentrada.

- Modelar a câmera apenas com a pirâmide estendendo-se ao infinito cria problemas: a projeção de pontos muito próximos ao centro $C$ gera divisões por zero e pontos muito distantes causam erros de precisão numérica. Para resolver isso, definimos dois planos paralelos ao plano de projeção: o **plano anterior**, situado a uma distância $n$ de $C$, e o **plano posterior**, situado a uma distância $f$. Idealmente, o plano anterior é o plano mais próximo da câmera, e o posterior o mais distance. Queremos que o plano de projeção esteja entre esses dois planos, onde todos eles estão na frente do centro de projeção.

- Ao cortar a pirâmide de visão pelos planos anterior e posterior, temos agora um **tronco de pirâmide** ou **frustum** que chamamos de **volume de visão**. Só veremos na câmera o que estiver dentro dele, pois descartaremos o que estiver fora.

## 2 - Normalização

- A pirâmide de visão pode ser torta dependendo dos parâmetros da câmera, por isso, aplicamos uma transformação de normalização nela, fazendo um cisalhamento e escala para ela se tornar uma pirâmide reta e simétrica. Seja $(I_u,I_v)$ o centro da tela virtual, onde definimos metade das dimensões de largura dela como $s_u,s_v$. Com isso, primeiro deslocamos as coordenadas de acordo com a seguinte matriz:

$M_1 = \begin{bmatrix} 1 & 0 & \frac{-I_u}{d} & 0 \\\ 0 & 1 & \frac{-I_v}{d} & 0 \\\ 0 & 0 & 1 & 0 \\\ 0 & 0 & 0 & 1 \end{bmatrix}$

- Podemos ver que ela faz um ponto $(u,v,z)$ ser deslocado de modo que ele permaneça na mesma coordenada $z$, porém suas coordenadas $x,y$ são deslocadas de modo que o centro da imagem coincida com o eixo ótico.

- Agora, faremos uma escala para a região da pirâmide na coordenada $z$ paralela ao plano de projeção ser dada por $\{(x,y) : -z \leq x \leq z, -z \leq y \leq z\}$, também normalizando de modo que o plano posterior esteja em $z=1$. Para isso, multiplicaremos pela matriz:

$M_2 = \begin{bmatrix} \frac{d}{s_u \cdot f} & 0 & 0 & 0 \\\ 0 & \frac{d}{s_v \cdot f} & 0 & 0 \\\ 0 & 0 & \frac{1}{f} & 0 \\\ 0 & 0 & 0 & 1 \end{bmatrix}$

- Dadas essas transformações, nossa câmera agora enxerga uma pirâmide de base quadrada com lado 2 e altura 1, cortada pelo plano anterior em algum local de topo, no plano anterior pós normalização.

- Por fim, faremos uma transformação para um **espaço de visibilidade**, criado para determinarmos rapidamente quais os objetos estão na frente dos outros, na ocasião de objetos no mundo tampando os outros. Sem um sistema de coordenadas apropriado, isso é computacionalmente caro.

- Retomando o nosso espaço normalizado, temos o espaço $\{(x,y,z) : -z \leq x \leq z, -z \leq y \leq z, \frac{n}{f} \leq z \leq 1\}$. A transformação tem o objetivo de levar os quatro pontos $(-\frac{n}{f},-\frac{n}{f},\frac{n}{f}),(\frac{n}{f},-\frac{n}{f},\frac{n}{f}),(-\frac{n}{f},\frac{n}{f},\frac{n}{f}),(\frac{n}{f},\frac{n}{f},\frac{n}{f})$ para as coordenadas $(-1,-1,0),(1,-1,0),(-1,1,0),(1,1,0)$, arrastando o restante do espaço junto a eles, deformando nosso frustum em um paralelepípedo.

- Precisamos primeiro levar a coordenada $z=\frac{n}{f}$ para $z=0$. Seja $z_0=\frac{n}{f}$. Podemos fazer isso de muitas formas, mas veja que precisamos fixar o plano posterior para que ele permaneça no mesmo local, e além disso, as paredes da pirâmide precisam se tornar retas paralelas para facilitar o cálculo de pertencimento à região de visão. Faremos isso com a matriz de transformação:

$T = \begin{bmatrix} 1 & 0 & 0 & 0 \\\ 0 & 1 & 0 & 0 \\\ 0 & 0 & \frac{1}{1-z_0} & \frac{-z_0}{1 - z_0} \\\ 0 & 0 & 1 & 0 \end{bmatrix}$

- Veja que essa transformação faz o deslocamento do espaço um pouco para trás e depois o expande para preservar a posição do plano posterior enquanto leva o anterior para zero. Porém, ainda temos um formato de frustum, e não um paralelepípedo. Para corrigir isso, guardaremos em cada ponto seu valor antigo da coordeanda $z$ na quarta dimensão adicional $w$. Isso acontece pois com essa informação, agora podemos usar o OpenGL para dividir as coordenadas dos eixos $X,Y$ por o valor guardado da coordeanda $z$, que tem o efeito de levar as bordas da pirâmide às bordas do paralelepípedo, como queríamos.

- Dado o espaço de visualização, um objeto ser visível implica que suas coordenadas $(x,y,z)$ pós processamento do OpenGL obedecem $x \in [-1,1], y \in [-1,1], z \in [0,1]$, que pode ser feito facilmente pelo computador em um tempo rápido. Além disso, o objeto visível em caso de sobreposições será aquele com menor coordenada $z$ entre as opções com mesmo par $(x,y)$.

## 3 - Representações

- Agora que sabemos a matemática por trás da projeção, vamos partir para os requisitos da implementação. Podemos definir unicamente uma câmera em um cenário a partir dos seguintes parâmetros:

    - O **centro de projeção** $C$

    - O **vetor de eixo ótico** $N$

    - O **vetor de inclinação** $V$

    - A **distância do plano anterior** $n$

    - A **distância do plano posterior** $f$

    - A **distância focal** $d$

    - Os **vértices da tela virtual** $(u_{min},v_{min}),(u_{max},v_{max})$

- Sob a restrição:

    - $N - \alpha V \neq 0, \forall \alpha$

- Também podemos definir a câmera a partir de um modelo de alto nível, que é mais intuitivo, mas também é mais restrito, modelando uma câmera simétrica com distância focal igual a distância ao plano anterior. Essas câmeras são as mais utilizadas em cenários reais de uso. Nesse caso, basta definir os seguintes parâmetros.

    - O **centro de projeção** $C$

    - O **vetor do eixo ótico** $N$

    - O **vetor de inclinação** $V$

    - A **distância do plano anterior** $n$

    - A **distância do plano posterior** $f$

    - O **campo de visão** $FOV$

    - A **proporção da imagem** $ASPECT$

- Sob a restrição:

    - $N - \alpha V \neq 0, \forall \alpha$

## 4 - Simulação

- Para começar a simulação, precisamos definir onde serão guardados os parâmetros. Para isso, existirá um arquivo `parameters.py` que descreve uma classe `Parameters` que guardará todos os parâmetros de representação mencionados na seção 3. Como vamos lidar com as duas representações de câmera, atualizaremos o método `__setitem__` para que ele atualize a relação entre os parâmetros `fov, aspect, u_min, v_min, u_max, v_max, d` conforme são atualizados. Também faremos um método `restrict` que altera os parâmetros para que a câmera agora obedeça as condições alcançáveis pela representação restrita.

- Agora, no arquivo `camera.py`, vamos criar a classe `VirtualCamera`, que representa a câmera virtual sendo calculada passo a passo. Ela é composta principalmente pelas seguintes funções:

    - `get_orthonormal_base`: Método que realiza o primeiro processo da normalização, fazendo o algoritmo de **ortonormalização de Gram-Schmidt** para obter a **base ortonormal** $\{u,v,n\}$ que descreve o **espaço da câmera virtual**.

    - `get_view_matrix`: Método que constroi e retorna a **matriz de visualização** $M_V$, que é a matriz de mudança de base que leva objetos do **espaço do mundo** para o **espaço da câmera virtual** descrito pela base ortonormal criada pelo método anterior.

    - `get_normalization_matrix`: Método que constroi e retorna as **matrizes de cisalhamento, escala e transformação projetiva** $M_1, M_2, T$ descritas no documento.

    - `get_full_projection_matrix`: Retorna a matriz resultante do processo total de projeção $T \cdot M_2 \cdot M_1$.

- Ainda no `camera.py`, temos a classe `Observer`, que lida com a câmera observadora. Em particular, ela tem as funções de movimentação para permitir que o usuário consiga se mover como observador na simulação. Ela se resume a uma implementação básica com alguns valores *hardcoded* arbitrários. 

- Seguindo, temos o arquivo `geometry.py`, responsável pela parte geométrica de obter e enviar coordenadas de desenho das câmeras. Ele possui dentro dele as funções a seguir:

    - `get_frustum_corners`: Método que calcula e retorna as 8 coordenadas do frustum no espaço do mundo que serão usadas para desenhar o frustum na câmera do observador externo.

    - `draw_virtual_camera`: Desenha a estrutura da câmera virtual no espaço do observador externo.

    - `draw_origin_axis`: Desenha os três eixos $x,y,z$ na origem no observador externo.

    - `draw_xz_grid`: Desenha uma grade quadriculada no plano gz para melhor ambientação.

- O arquivo `objects.py` é um arquivo que descreve objetos 3D para serem colocados no espaço do mundo, fornecendo mais conteúdos para observar como a câmera se comporta de acordo com a geometria e distorções feitas pelos parâmetros.

- Além desses, temos o arquivo `gui.py`, responsável pela interface gráfica de usuário para variação dos parâmetros e controle do cenário. Ele contém classes que representam os elementos da GUI como `Button` e `Slider` e também funções auxiliares para fazer a GUI de forma mais fácil, mas não é relevante para o entendimento de como a câmera funciona de fato. 

- Finalmente, temos o arquivo `main.py`, responsável por inicializar o simulador, gerenciar os eventos de input e juntar os outros arquivos, fazendo-os interagir entre si. Dê uma olhada!
