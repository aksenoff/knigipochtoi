update Книга
set Поставщик = (select Имя from Поставщик order by random() limit 1) 