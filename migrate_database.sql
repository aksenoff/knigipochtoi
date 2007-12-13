insert into Книга
(id,Категория,Название,Автор,ISBN, Переплет,Год_издания,Количество_страниц,Цена, Аннотация, Обложка)
select id, category as Категория, title as Название, authors as Автор, ISBN, cover as Переплет,
year as Год_издания, pages as Количество_страниц, price as Цена, description as Аннотация, image as Обложка 
from Books;