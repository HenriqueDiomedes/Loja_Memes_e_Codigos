from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse
from django.contrib import messages
from .models import Produto
from .models import Cliente
from django.db.models import Q
import mercadopago
from django.conf import settings


#função para permisão de administrador
def verificar_grupo(usuario):
    return usuario.groups.filter(name='funcionario').exists()


#Funções sobre produtos:


#função para cadastrar produtos
@user_passes_test(verificar_grupo)
def cadastroProduto(request):
    if request.method == 'POST':
        print("Dados recebidos com sucesso")
       
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco')
        quantidade = request.POST.get('quantidade')

        imagem1 = request.FILES.get('imagem1')
        imagem2 = request.FILES.get('imagem2')
        imagem3 = request.FILES.get('imagem3')
        
        produto = Produto()
        produto.nome = nome
        produto.descricao = descricao
        produto.preco = preco
        produto.quantidade = quantidade
        
        produto.imagem1 = imagem1
        produto.imagem2 = imagem2
        produto.imagem3 = imagem3

        produto.save()
    
    return render(request, 'cadastro_produto.html')










 # sobre prooduto (tela de cadastro de produtos)

# função que mostra a lista dos produtos(tela inicial)

def lista_Produtos(request):
    nome_produto = request.GET.get('nome_produto')
    valor_min = request.GET.get('valor_min')
    valor_max = request.GET.get('valor_max')
    ordem = request.GET.get('ordem')

    print("Produto pesquisado: ", nome_produto)

    produtos = Produto.objects.all()

    # Filtro por nome ou descrição (parte do texto)
    if nome_produto:
        produtos = produtos.filter(
            Q(nome__icontains=nome_produto) |
            Q(descricao__icontains=nome_produto)
        )

    # Filtro por preço
    if valor_min and valor_max:
        try:
            valor_min = float(valor_min)
            valor_max = float(valor_max)
            produtos = produtos.filter(preco__range=(valor_min, valor_max))
        except ValueError:
            pass  # ignora filtro de preço se não for número válido

    # Ordenação
    if ordem:
        if ordem == '1':
            produtos = produtos.order_by("nome")
        elif ordem == '2':
            produtos = produtos.order_by("preco")
        elif ordem == '3':
            produtos = produtos.order_by("-nome")
        elif ordem == '4':
            produtos = produtos.order_by("-preco")

    return render(request, 'lista_produtos.html', {'produtos': produtos})

#função que mostra os detalhes do produto
def detalhesProduto(request, id):
    print(id)
    produto = get_object_or_404(Produto, pk=id)

    imagens = []
    if produto.imagem1:
        imagens.append(produto.imagem1.url)
    if produto.imagem2:
        imagens.append(produto.imagem2.url)
    if produto.imagem3:
        imagens.append(produto.imagem3.url)

    return render(request, "detalhes_produto.html", {"produto": produto, "imagens": imagens})

#fução que mostra o estoque de produtos(com osções de cadastrar/atualizar/deletar)
@user_passes_test(verificar_grupo)
def admEstoque(request):
    produtos = Produto.objects.all()
    return render(request, 'adm_estoque.html', {'produtos': produtos})

#função para deletar algum produto
def deletarProduto(request, id):
    produto = get_object_or_404(Produto, pk=id)
    produto.delete()

    return redirect('adm_estoque')

# função para atualizar um produto selecionado
@user_passes_test(verificar_grupo)
def atualizarProduto(request):
    produto = None  # Inicializa a variável para evitar erro caso o ID não seja encontrado

    if request.method == "GET":
        produto_id = request.GET.get("id_produto")
        if produto_id:
            produto = Produto.objects.filter(id=produto_id).first()

    if request.method == "POST":
        produto_id = request.POST.get("id_produto")

        if not produto_id:
            return HttpResponse("Erro: ID do produto não encontrado.", status=400)

        try:
            produto = Produto.objects.get(id=produto_id)
        except Produto.DoesNotExist:
            return HttpResponse("Erro: Produto não encontrado.", status=404)

        # Atualiza os campos básicos
        produto.nome = request.POST.get("nome") or produto.nome
        produto.descricao = request.POST.get("descricao") or produto.descricao

        # Atualiza o preço, tratando vírgula como separador decimal
        preco = request.POST.get("preco")
        if preco:
            try:
                preco = preco.replace(',', '.')
                produto.preco = Decimal(preco)
            except InvalidOperation:
                return HttpResponse("Erro: O preço deve ser um número válido.", status=400)

        # Atualiza a quantidade
        quantidade = request.POST.get("quantidade")
        if quantidade:
            try:
                produto.quantidade = int(quantidade)
            except ValueError:
                return HttpResponse("Erro: A quantidade deve ser um número inteiro.", status=400)

        # Atualiza as imagens se forem enviadas
        if 'imagem1' in request.FILES:
            produto.imagem1 = request.FILES['imagem1']
        if 'imagem2' in request.FILES:
            produto.imagem2 = request.FILES['imagem2']
        if 'imagem3' in request.FILES:
            produto.imagem3 = request.FILES['imagem3']

        produto.save()
        return redirect('adm_estoque')

    return render(request, "atualizar_produto.html", {"produto": produto})

 # sobre clientes (tela de cadastro de clientes)



#FUNÇÕES SOBRE CLINTES

#função para cadastrar clientes
def cadastroCliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('cadastro_cliente')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Já existe um usuário com este e-mail.')
            return redirect('cadastro_cliente')

        usuario = User.objects.create_user(username=email, email=email, password=senha)
        usuario.first_name = nome
        usuario.last_name = sobrenome
        usuario.save()

        cliente = Cliente(
            idUsuario=usuario,
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            telefone=request.POST.get('telefone'),
            cpf=request.POST.get('cpf'),
            dataNascimento=request.POST.get('dataNascimento'),
            cep=request.POST.get('cep'),
            rua=request.POST.get('rua'),
            numero_casa=request.POST.get('numero_casa'),
            cidade=request.POST.get('cidade'),
            estado=request.POST.get('estado')
        )
        cliente.save()

        return redirect('lista_produtos')

    return render(request, 'cadastro_cliente.html')

#função para editar o cadastro do cliente
def atualizarCliente(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        cliente = Cliente.objects.get(idUsuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('cadastro_cliente')  # Redireciona para o cadastro se ainda não existir

    if request.method == 'POST':
        cliente.nome = request.POST.get('nome')
        cliente.sobrenome = request.POST.get('sobrenome')
        cliente.email = request.POST.get('email')
        cliente.telefone = request.POST.get('telefone')
        cliente.cpf = request.POST.get('cpf')
        cliente.dataNascimento = request.POST.get('dataNascimento')
        cliente.rua = request.POST.get('rua')
        cliente.numero_casa = request.POST.get('numeroCasa')
        cliente.cep = request.POST.get('cep')
        cliente.estado = request.POST.get('estado')
        cliente.cidade = request.POST.get('cidade')
        cliente.save()
        return redirect('perfil_cliente')  # Redireciona para a página de perfil

    return render(request, 'atualizar_cliente.html', {'cliente': cliente})

#função de excluir cliente
def excluirConta(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        user = request.user
        try:
            cliente = Cliente.objects.get(idUsuario=user)
            cliente.delete()
        except Cliente.DoesNotExist:
            pass
        user.delete()  # Deleta o usuário do sistema
        return redirect('login')  # Redireciona para a tela de login após a exclusão

    return render(request, 'excluirConta.html')

#função para chamar o administrador de clientes
@user_passes_test(verificar_grupo)
def adm_cliente(request):
    clientes = Cliente.objects.all()  # Carrega todos os clientes do banco de dados

    return render(request, 'adm_cliente.html', {'clientes': clientes})

# função para exibir o perfil do cliente
def perfilCliente(request):
    if not request.user.is_authenticated:
        return redirect('login')
    print(request.user)  # Verifique qual usuário está autenticado

    try:
        cliente = Cliente.objects.get(idUsuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('cadastro_cliente')  # Se não encontrar, redireciona para o cadastro
    print(cliente)  
    return render(request, 'perfil_cliente.html', {'cliente': cliente})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        senha = request.POST['senha']
        user = authenticate(request, username=username, password=senha)
        if user:
            login(request, user)
            return redirect('perfilCliente')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')






# acessar a página inicial ( tela Mais 'formularios')
@user_passes_test(verificar_grupo)
def formulario(request):
    if request.method == 'POST':
        escolha = request.POST.get('escolha')
        if escolha == 'produto':
            return redirect('cadastro_produto')
        elif escolha == 'cliente':
            return redirect('cadastro_cliente')
        elif escolha == 'atualizar':
            return redirect('atualizar_produto')
        elif escolha == 'perfil':
            return redirect('perfilcliente')
        elif escolha == 'estoque':
            return redirect('adm_estoque')
        
    return render(request, 'formulario.html')


#FUNÇÕES SOBRE VENDAS

# Função para gerar o pagamento no Mercado Pago
  # ou ajuste conforme o local do seu modelo Produto

@user_passes_test(verificar_grupo)
def formularioPagamento(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        messages.error(request, "Carrinho vazio!")
        return redirect('exibir_carrinho')

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    items = []
    for produto_id, item in carrinho.items():
        produto = Produto.objects.get(id=produto_id)
        items.append({
            "title": produto.nome,
            "quantity": item['quantidade'],
            "unit_price": float(item['preco']),
            "currency_id": "BRL"
        })

    preference_data = {
        "items": items,
        "back_urls": {
            "success": "http://127.0.0.1:8000/pagamento/sucesso/",
            "failure": "http://127.0.0.1:8000/pagamento/falha/",
            "pending": "http://127.0.0.1:8000/pagamento/pendente/",
        },
        "auto_return": "approved",
        "statement_descriptor": "MEMES&CÓDIGOS"  # opcional
    }

    preference_response = sdk.preference().create(preference_data)

    if preference_response["status"] == 201:
        return redirect(preference_response["response"]["init_point"])
    else:
        messages.error(request, "Erro ao criar a preferência de pagamento!")
        return redirect('exibir_carrinho')

def pagamento_sucesso(request):
    """
    Exibe uma página de sucesso quando o pagamento é completado com sucesso.
    """
    return render(request, 'pagamento_sucesso.html')

def pagamento_falha(request):
    """
    Exibe uma página quando o pagamento falha.
    """
    return render(request, 'pagamento_falha.html')

def pagamento_pendente(request):
    """
    Exibe uma página quando o pagamento está pendente.
    """
    return render(request, 'pagamento_pendente.html')


#formulario para adicionar produto ao carrinho
def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = request.session.get('carrinho', {})

    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] += 1
    else:
        carrinho[str(produto_id)] = {
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade': 1,
            'imagem': produto.imagem1.url if produto.imagem1 else '/static/img/sem-imagem1.png',
        }

    request.session['carrinho'] = carrinho
    return redirect('exibir_carrinho')

#formulario para remover produto do carrinho
def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    if str(produto_id) in carrinho:
        del carrinho[str(produto_id)]
        request.session['carrinho'] = carrinho
    return redirect('exibir_carrinho')

#formulario para exibir produto no carrinho
def exibir_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    produtos = []
    total_geral = 0

    for produto_id, item in carrinho.items():
        try:
            produto = Produto.objects.get(id=produto_id)
            quantidade = item.get('quantidade', 1)
            total = produto.preco * quantidade

            produtos.append({
                'id': produto.id,
                'nome': produto.nome,
                'descricao': produto.descricao,
                'imagem1': produto.imagem1.url if produto.imagem1 else '',
                'preco': produto.preco,
                'quantidade': quantidade,
                'total': total
            })

            total_geral += total
        except Produto.DoesNotExist:
            pass

    return render(request, 'carrinho.html', {
        'produtos': produtos,
        'total_geral': total_geral
    })

#aumentar quantidade de produtos no carrinho
def aumentar_quantidade(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] += 1
    request.session['carrinho'] = carrinho
    return redirect('exibir_carrinho')

#diminr quantidade de produtos no carrinho
def diminuir_quantidade(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    if str(produto_id) in carrinho:
        if carrinho[str(produto_id)]['quantidade'] > 1:
            carrinho[str(produto_id)]['quantidade'] -= 1
        else:
            del carrinho[str(produto_id)]
    request.session['carrinho'] = carrinho
    return redirect('exibir_carrinho')

#finalizar compra
def finalizar_compra(request):
    return render(request, 'finalizar_compra.html')









# função para a tela de login
def login(request):   
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

    return render(request, 'registration/login.html')
 
def perfilCliente(request):
    return render(request,'perfil_cliente.html')

def home(request):
    return render(request,'home.html')

@login_required
def privado(request):
    return render(request,'privado.html')

@user_passes_test(verificar_grupo)
def funcionario(request):
    return render(request,'funcionario.html')

 