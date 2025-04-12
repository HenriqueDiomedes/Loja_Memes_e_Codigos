# Create your models here.
from django.db import models  
from django.contrib.auth.models import User

class Produto(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.CharField(max_length=255, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)   #blank=True, null=True
    quantidade = models.IntegerField()
    
    imagem1 = models.ImageField(upload_to='static/img/produto/', null=True, blank=True)
    imagem2 = models.ImageField(upload_to='static/img/produto/', null=True, blank=True)
    imagem3 = models.ImageField(upload_to='static/img/produto/', null=True, blank=True)

class Cliente(models.Model):
    idUsuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, default='000.000.000-00')
    dataNascimento = models.DateField(null=True, blank=True)
    nome = models.CharField(max_length=100, default='Nome Desconhecido')
    sobrenome = models.CharField(max_length=100, default='Sobrenome')
    email = models.CharField(max_length=50, default='email@exemplo.com')
    telefone = models.CharField(max_length=15, default='(00)00000-0000')
    numero_casa = models.CharField(max_length=50, default='S/N')
    cep = models.CharField(max_length=9, default='00000-000')
    rua = models.CharField(max_length=50, default='Rua Desconhecida')
    cidade = models.CharField(max_length=50, default='Cidade Desconhecida')
    estado = models.CharField(max_length=20, default='Estado')



    