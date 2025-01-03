# pip modüllerini import ediyoruz
import time
import pyfiglet
import inquirer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from tinydb import TinyDB, Query

# isNaN fonksiyonunu tanımlıyoruz (js alışkanlığı)
def isNaN(value):
    try:
        float(value)
        return False
    except ValueError:
        return True

# konsol için rich kütüphanesini kullanıyoruz
console = Console()

# TinyDB veri tabanlarını tanımlıyoruz
db_products = TinyDB('products.json')
db_users = TinyDB('users.json')
db_admins = TinyDB('admins.json')
Product = Query()
User = Query()
Admin = Query()


# YÖNETİCİ


sifreDeneme = 0

# yönetici girişi
def admin_menu():
    global sifreDeneme
    if sifreDeneme == 0:
        console.print(Panel("[bold green]Yönetici Menüsü[/]", expand=False))
    admin = db_admins.all()

    # eğer yönetici yoksa, yönetici oluşturulmasını sağlıyoruz
    if len(admin) == 0:
        admcreate = inquirer.prompt([inquirer.Text('password', message="Yönetici şifresi oluşturunuz")])
        db_admins.insert({'username': 'admin', 'password': admcreate['password']})
        console.print(Panel("[bold green]Yönetici şifresi oluşturuldu![/]", expand=False))
        time.sleep(2)
        console.clear()
        admin_menu()
    
    console.print("[bold] Kalan hakkınız: " + str(3 - sifreDeneme) + "[/]")
    sifre = inquirer.prompt([inquirer.Text('password', message="Şifre giriniz")])

    admin = db_admins.get(Admin.username == 'admin')
    if sifre['password'] == admin['password']:
        console.print(Panel("[bold green]Giriş başarılı![/]", expand=False))
        sifreDeneme = 0
        admin_menu_options()
    else:
        console.clear()
        console.print(Panel("[bold red]Hatalı şifre![/]", expand=False))
        sifreDeneme += 1
        if sifreDeneme == 3:
            console.print(Panel("[bold red]3 defa hatalı giriş yaptınız. 2 saniye içinde ana menüye dönülüyor![/]", expand=False))
            sifreDeneme = 0
            time.sleep(2)
            main()
        else:
            admin_menu()

# yönetici menüsü
def admin_menu_options():
    console.clear()
    console.print(Panel("[bold green]Yönetici Menüsü[/]", expand=False))
    while True:
        choice = inquirer.prompt([inquirer.List('option', message="Ne yapmak istersiniz?", choices=['Ürün ekle', 'Ürün sil', 'Ürün güncelle', 'Ürün listele', 'Ana menü'])])
        if choice['option'] == 'Ürün ekle':
            add_product()
        elif choice['option'] == 'Ürün sil':
            delete_product()
        elif choice['option'] == 'Ürün güncelle':
            update_product()
        elif choice['option'] == 'Ürün listele':
            list_products()
        else:
            main()

# veritabanına ürün ekleme
def add_product():
    console.clear()
    console.print(Panel("[bold green]Ürün Ekle[/]", expand=False))
    product_name = inquirer.prompt([inquirer.Text('name', message="Ürün adı")])
    product_price = inquirer.prompt([inquirer.Text('price', message="Ürün fiyatı")])
    if isNaN(product_price['price']):
        console.print(Panel("[bold red]Hatalı fiyat girişi![/]", expand=False))
        time.sleep(2)
        add_product()
    product_adet = inquirer.prompt([inquirer.Text('adet', message="Ürün adedi")])
    if isNaN(product_adet['adet']):
        console.print(Panel("[bold red]Hatalı adet girişi![/]", expand=False))
        time.sleep(2)
        add_product()

    db_products.insert({'name': product_name['name'], 'price': product_price['price'], 'adet': product_adet['adet']})
    console.print(Panel("[bold green]Ürün başarıyla eklendi![/]", expand=False))
    admin_menu_options()

# veritabanından ürün silme
def delete_product():
    console.clear()
    console.print(Panel("[bold green]Ürün Sil[/]", expand=False))
    products = db_products.all()
    if len(products) == 0:
        console.print(Panel("[bold red]Silinecek ürün bulunamadı! Ana menüye dönülüyor...[/]", expand=False))
        time.sleep(2)
        admin_menu_options()
    product_names = [product['name'] for product in products]
    product_name = inquirer.prompt([inquirer.List('name', message="Ürün seçiniz", choices=product_names)])
    db_products.remove(Product.name == product_name['name'])
    console.print(Panel(f"[bold green]{product_name['name']} başarıyla silindi![/]", expand=False))
    admin_menu_options()

# veritabanındaki ürünleri güncelleme
def update_product():
    console.clear()
    console.print(Panel("[bold green]Ürün Güncelle[/]", expand=False))
    products = db_products.all()
    if len(products) == 0:
        console.print(Panel("[bold red]Güncellenecek ürün bulunamadı! Ana menüye dönülüyor...[/]", expand=False))
        time.sleep(2)
        admin_menu_options()
    product_names = [product['name'] for product in products]
    urun = inquirer.prompt([inquirer.List('name', message="Ürün seçiniz", choices=product_names)])
    table = Table(title="Ürün Bilgileri")
    table.add_column("No", justify="center", style="bold")
    table.add_column("Ürün Adı", justify="center", style="cyan") 
    table.add_column("Fiyat", justify="right")
    table.add_column("Adet", justify="right")
    
    selected_product = db_products.search(Product.name == urun['name'])[0]
    table.add_row(str(selected_product.doc_id + 1) ,selected_product['name'], selected_product['price'] + " TL", selected_product['adet'])
    console.print(table)

    guncellenecek = inquirer.prompt([inquirer.List('update', message="Hangi bilgiyi güncellemek istersiniz?", choices=['Fiyat', 'Adet', 'İptal'])])
    if guncellenecek['update'] == 'Fiyat':
        product_price = inquirer.prompt([inquirer.Text('price', message="Yeni fiyat giriniz")])
        if isNaN(product_price['price']):
            console.print(Panel("[bold red]Hatalı fiyat girişi![/]", expand=False))
            time.sleep(1)
            update_product()
        db_products.update({'price': product_price['price']}, Product.name == urun['name'])
        console.print(Panel("[bold green]Fiyat başarıyla güncellendi![/]", expand=False))
        time.sleep(2)
        admin_menu_options()
    elif guncellenecek['update'] == 'Adet':
        product_adet = inquirer.prompt([inquirer.Text('adet', message="Yeni adet giriniz")])
        if isNaN(product_adet['adet']):
            console.print(Panel("[bold red]Hatalı adet girişi![/]", expand=False))
            time.sleep(1)
            update_product()
        db_products.update({'adet': product_adet['adet']}, Product.name == urun['name'])
        console.print(Panel("[bold green]Adet başarıyla güncellendi![/]", expand=False))
        time.sleep(2)
        admin_menu_options()
    else:
        admin_menu_options()

# veritabanındaki ürünleri listeleme
def list_products():
    console.clear()
    console.print(Panel("[bold green]Ürün Listesi[/]", expand=False))
    table = Table(title="Ürün Listesi")
    table.add_column("No", justify="center", style="bold")
    table.add_column("Ürün Adı", justify="left", style="cyan")
    table.add_column("Fiyat", justify="right")
    table.add_column("Adet", justify="right")
    products = db_products.all()
    no = 1
    for product in products:
        table.add_row(str(no) ,product['name'], product['price'] + " TL", product['adet'])
        no += 1
    console.print(table)
    menuye_don = inquirer.prompt([inquirer.List('don', message="Ana menüye dönmek için Enter'a basınız", choices=['Ana menü'])])
    if(menuye_don):
        admin_menu_options()


# KULLANICI


mevcut_kullanici = ""

# kullanıcı auth menü
def customer_menu():
    console.clear()
    console.print(Panel("[bold green]Müşteri Menüsü[/]", expand=False))
    choice = inquirer.prompt([inquirer.List('option', message="Ne yapmak istersiniz?", choices=['Giriş yap', 'Kayıt ol', 'Ana menü'])])
    if choice['option'] == 'Giriş yap':
        login()
    elif choice['option'] == 'Kayıt ol':
        register()
    else:
        main()

# kullanıcı girişi
def login():
    console.clear()
    console.print(Panel("[bold green]Giriş Yap[/]", expand=False))
    global mevcut_kullanici
    username = inquirer.prompt([inquirer.Text('username', message="Kullanıcı adı")])
    password = inquirer.prompt([inquirer.Text('password', message="Şifre")])
    user = db_users.search(User.username == username['username'])
    if user:
        if user[0]['password'] == password['password']:
            console.print(Panel("[bold green]Giriş başarılı![/]", expand=False))
            mevcut_kullanici = username['username']
            customer_menu_options()
        else:
            console.print(Panel("[bold red]Hatalı şifre![/]", expand=False))
            time.sleep(2)
            customer_menu()
    else:
        console.print(Panel("[bold red]Kullanıcı bulunamadı![/]", expand=False))
        time.sleep(2)
        customer_menu()

# kullanıcı kayıt
def register():
    console.clear()
    console.print(Panel("[bold green]Kayıt Ol[/]", expand=False))
    username = inquirer.prompt([inquirer.Text('username', message="Kullanıcı adı")])
    password = inquirer.prompt([inquirer.Text('password', message="Şifre")])
    db_users.insert({'username': username['username'], 'password': password['password'], 'orders': []})
    console.print(Panel("[bold green]Kayıt işlemi başarılı![/]", expand=False))
    time.sleep(2)
    customer_menu()

# kullanıcı ana menü
def customer_menu_options():
    console.clear()
    global mevcut_kullanici
    console.print(Panel("[bold green]Müşteri Menüsü[/]", expand=False))
    while True:
        choice = inquirer.prompt([inquirer.List('option', message="Ne yapmak istersiniz?", choices=['Sipariş ver', 'Siparişlerimi gör', 'Çıkış'])])
        if choice['option'] == 'Sipariş ver':
            place_order()
        elif choice['option'] == 'Siparişlerimi gör':
            list_orders()
        else:
            mevcut_kullanici = ""
            main()

# sipariş ekleme sistemi
busiparis = []
def place_order():
    console.clear()
    console.print(Panel("[bold green]Sipariş Ver[/]", expand=False))
    global busiparis
    products = db_products.all()
    if len(products) == 0:
        console.print(Panel("[bold red]Sipariş verilecek ürün bulunamadı! Ana menüye dönülüyor...[/]", expand=False))
        time.sleep(2)
        customer_menu_options()
    table = Table(title="Ürün Listesi")
    table.add_column("No", justify="center", style="bold")
    table.add_column("Ürün Adı", justify="left", style="cyan")
    table.add_column("Fiyat", justify="right")
    table.add_column("Adet", justify="right")
    no = 1
    for product in products:
        table.add_row(str(no) ,product['name'], product['price'] + " TL", product['adet'])
        no += 1
    console.print(table)
    
    product_choices = [product['name'] for product in products]
    product_choices.append('Çıkış')
    urun = inquirer.prompt([inquirer.List('name', message="Ürün seçiniz", choices=product_choices)])
    
    if urun['name'] == 'Çıkış':
        customer_menu_options()

    adet = inquirer.prompt([inquirer.Text('quantity', message="Adet giriniz")])
    if isNaN(adet['quantity']):
        console.print(Panel("[bold red]Hatalı adet girişi![/]", expand=False))
        time.sleep(2)
        place_order()
    if int(adet['quantity']) <= 0:
        console.print(Panel("[bold red]Adet 0'dan büyük olmalıdır![/]", expand=False))
        time.sleep(2)
        place_order()
    selected_product = db_products.search(Product.name == urun['name'])[0]
    if int(adet['quantity']) > int(selected_product['adet']):
        console.print(Panel("[bold red]Stokta yeterli ürün bulunmamaktadır![/]", expand=False))
        time.sleep(2)
        place_order()
    price = float(selected_product['price']) * int(adet['quantity'])
    order_data = {
        'product': urun['name'],
        'quantity': adet['quantity'],
        'price': price
    }
    busiparis.append(order_data)

    new_adet = int(selected_product['adet']) - int(adet['quantity'])
    db_products.update({'adet': str(new_adet)}, Product.name == urun['name'])
    ek_siparis = inquirer.prompt([inquirer.List('add', message="Başka ürün eklemek ister misiniz?", choices=['Evet', 'Hayır'])])
    if ek_siparis['add'] == 'Evet':
        place_order()
    else:
        order_summary(busiparis)

# sipariş özeti gösterme ve veritabanı kayıtları
def order_summary(siparisler):
    global busiparis
    busiparis = []
    console.clear()
    console.print(Panel("[bold green]Siparişiniz başarıyla alındı![/]", expand=False))
    ntable = Table(title="Sipariş Detayı")
    ntable.add_column("No", justify="center", style="bold")
    ntable.add_column("Ürün Adı", justify="left", style="cyan")
    ntable.add_column("Adet", justify="center")
    ntable.add_column("Birim Fiyat", justify="right")
    ntable.add_column("Toplam", justify="right")
    user = db_users.search(User.username == mevcut_kullanici)[0]
    toplam = 0
    indirim = 0
    no = 1

    for siparis in siparisler:
        birim_fiyat = float(siparis['price']) / float(siparis['quantity'])
        adet = int(siparis['quantity'])
        siparis_toplam = float(siparis['price'])
        toplam += siparis_toplam
        
        ntable.add_row(
            str(no),
            str(siparis['product']),
            str(siparis['quantity']),
            f"{birim_fiyat:.2f} TL",
            f"{siparis_toplam:.2f} TL"
        )
        no += 1
    
    if toplam > 500:
        indirim = toplam * 0.10
        ind = f"{-indirim:.2f}"
        siparisler.append({
            'product': 'İndirim', 
            'quantity': '1', 
            'price': str(ind)
        })
        toplam -= indirim
    
    user_orders = user.get('orders', [])
    user_orders.append(siparisler)
    db_users.update({'orders': user_orders}, User.username == mevcut_kullanici)
    console.print(ntable)
    if indirim > 0:
        console.print(Panel(f"[bold cyan]İndirimsiz Tutar: {(toplam + indirim):.2f} TL[/]", expand=False))
        console.print(Panel("[green]Toplam tutar 500 TL üzeri olduğu için %10 indirim uygulanmıştır![/]", expand=False))
    console.print(Panel(f"[bold green]Toplam Tutar: {toplam:.2f} TL[/]", expand=False))
    menuye_don = inquirer.prompt([inquirer.List('don', message="Ana menüye dönmek için Enter'a basınız", choices=['Ana menü'])])
    if menuye_don:
        customer_menu_options()
                      
# eski siparişleri listeleme
def list_orders():
    console.clear()
    console.print(Panel("[bold green]Siparişlerim[/]", expand=False))
    user = db_users.search(User.username == mevcut_kullanici)[0]
    orders = user.get('orders', [])
    
    if len(orders) == 0:
        console.print(Panel("[bold red]Sipariş bulunamadı![/]", expand=False))
        time.sleep(2)
        customer_menu_options()
    siparis_no = 1
    for siparis_grubu in orders:
        table = Table(title=f"Sipariş #{siparis_no}")
        table.add_column("No", justify="center", style="bold")
        table.add_column("Ürün Adı", justify="left", style="cyan")
        table.add_column("Adet", justify="center") 
        table.add_column("Birim Fiyat", justify="right")
        table.add_column("Toplam", justify="right")
        
        toplam = 0
        no = 1
        for siparis in siparis_grubu:
            if siparis['product'] != 'İndirim':
                birim_fiyat = float(siparis['price']) / float(siparis['quantity'])
                siparis_toplam = float(siparis['price'])
                toplam += siparis_toplam
                
                table.add_row(
                    str(no),
                    siparis['product'],
                    siparis['quantity'],
                    f"{birim_fiyat:.2f} TL",
                    f"{siparis_toplam:.2f} TL"
                )
                no += 1
            else:
                table.add_row(
                    "",
                    'İndirim',
                    '1',
                    '',
                    f"{siparis['price']} TL"
                )
                toplam += float(siparis['price'])
                
        console.print(table)
        console.print(Panel(f"[bold green]Toplam Tutar: {toplam:.2f} TL[/]", expand=False))
        console.print("\n")
        siparis_no += 1

    menuye_don = inquirer.prompt([inquirer.List('don', message="Ana menüye dönmek için Enter'a basınız", choices=['Ana menü'])])
    if menuye_don:
        customer_menu_options()




# main fonksiyonunu tanımlıyoruz
def main():
    console.clear()
    # başlığı oluşturuyoruz
    text = "Merhaba!"
    ascii_art = pyfiglet.figlet_format(text)
    console.print(ascii_art, style="bold magenta")
    console.print(Panel("[bold green]Mağaza Yönetim Sistemine hoş geldiniz.[/]", expand=False))

    # kullanıcı seçimi
    another = inquirer.prompt([inquirer.List('user', message="Hangi kullanıcı olarak giriş yapmak istiyorsunuz?", choices=['Yönetici', 'Müşteri', 'Çıkış'])])
    if another['user'] == 'Yönetici':
        console.clear()
        admin_menu()
    elif another['user'] == 'Müşteri':
        console.clear()
        customer_menu()
    else:
        console.clear()
        console.print(Panel("[bold green]Çıkış yaptınız.[/]", expand=False))
        exit()


# Programı çalıştırıyoruz
if __name__ == "__main__":
    main()