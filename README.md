# GameTameDealFinder
This is a suite of Python scripts intended to maximize [Steam Market](https://steamcommunity.com/market/search?appid=440) profit attained from the [GameTame](https://gametame.com/) offer-based site.  
  
GameTame is a site where one can trade in-site points for [TF2](http://www.teamfortress.com/) or [DOTA2](http://blog.dota2.com/?l=english) items.  
The aim of this project was to find discrepancies between the in-site item prices and the Steam Market item prices, so that it would be possible to trade for outliers on the site and sell them for profit on the Steam Market.
It works by maintaining a [MySQL](https://www.mysql.com/) database containing the information for every item provided on the site, and putting GameTame's "point price"  alongside the real price on the Steam Market so that discrepancies could be capitalized on.  
The Steam Market prices were updated frequently, and thus it became necessary to not only constantly update and study the results from the database, but also to study trends in the Market.  
In order for an item to be valuable, it not only had to have a good point price to market price ratio, but it also had to be sold consistently and reliably. Otherwise, I would end up with an item that I could not sell, and it would be a failed investment. As a result, I added a 'volume' column into the database which allowed me to see which items people were actually buying.
  
To get the Steam Market prices for each item, I originally intended to use 2 different sources: the actual Steam Market and the website [Backpack.tf](https://backpack.tf/). The reasoning behind using a source other than the Steam Market was the fact that the Steam Market API did not always return a price. For some items, it did not produce any information. However, Backpack.tf's prices were often far off from the actual prices, and as a result I stopped using it as a source.  
  
However, I eventually found out that GameTame updates its internal point prices every time one goes to purchase an item, and thus the entire concept was uprooted.  
Nonetheless, the experience gained from pursuing the project was invaluable.  
  
This project has been discontinued
