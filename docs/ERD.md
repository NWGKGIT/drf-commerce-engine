erDiagram
User {
  bigint id pk
  varchar password 
  timestamp_with_time_zone last_login 
  boolean is_superuser 
  varchar email 
  varchar first_name 
  varchar last_name 
  boolean is_staff 
  boolean is_active 
  timestamp_with_time_zone date_joined 
}
UserProfile {
  bigint id pk
  bigint user_id 
  date birth_date 
  varchar profile_picture 
  jsonb preferences 
  timestamp_with_time_zone updated_at 
}
Address {
  bigint id pk
  bigint user_id 
  varchar address_line_1 
  varchar address_line_2 
  varchar city 
  varchar region 
  varchar postal_code 
  varchar country 
  jsonb location_pin 
  boolean is_default 
  timestamp_with_time_zone created_at 
}
Cart {
  bigint id pk
  bigint user_id 
  timestamp_with_time_zone created_at 
  timestamp_with_time_zone updated_at 
}
CartItem {
  bigint id pk
  bigint cart_id 
  bigint product_id 
  integer quantity 
  timestamp_with_time_zone created_at 
}
Payment {
  bigint id pk
  bigint order_id 
  varchar reference 
  numeric amount 
  varchar currency 
  varchar status 
  varchar provider 
  jsonb raw_response 
  timestamp_with_time_zone created_at 
  timestamp_with_time_zone updated_at 
}
Category {
  bigint id pk
  bigint parent_category_id 
  varchar name 
  varchar slug 
  text description 
  boolean is_active 
  timestamp_with_time_zone created_at 
}
Product {
  bigint id pk
  bigint category_id 
  varchar name 
  varchar slug 
  text description 
  varchar sku 
  numeric price 
  numeric discount_price 
  varchar currency 
  jsonb specifications 
  boolean is_featured 
  boolean is_active 
  timestamp_with_time_zone created_at 
  timestamp_with_time_zone updated_at 
}
ProductImage {
  bigint id pk
  bigint product_id 
  varchar image_url 
  varchar alt_text 
  boolean is_main 
  integer position 
  timestamp_with_time_zone created_at 
}
Review {
  bigint id pk
  bigint user_id 
  bigint product_id 
  integer rating 
  text comment 
  boolean is_verified_purchase 
  timestamp_with_time_zone created_at 
}
Wishlist {
  bigint id pk
  bigint user_id 
  timestamp_with_time_zone created_at 
}
WishlistItem {
  bigint id pk
  bigint wishlist_id 
  bigint product_id 
  timestamp_with_time_zone added_at 
}
InventoryItem {
  bigint id pk
  bigint product_id 
  integer quantity 
  varchar location 
  timestamp_with_time_zone last_updated 
}
InventoryReservation {
  bigint id pk
  bigint cart_id 
  bigint order_id 
  bigint product_id 
  integer quantity 
  timestamp_with_time_zone expires_at 
  timestamp_with_time_zone created_at 
}
Address }|--|| User: ""
Cart ||--|| User: ""
Category }|--|| Category: ""
InventoryItem }|--|| Product: ""
Payment }|--|| Order: ""
Product }|--|| Category: ""
ProductImage }|--|| Product: ""
UserProfile ||--|| User: ""
Wishlist ||--|| User: ""
CartItem }|--|| Cart: ""
CartItem }|--|| Product: ""
Review }|--|| User: ""
Review }|--|| Product: ""
WishlistItem }|--|| Wishlist: ""
WishlistItem }|--|| Product: ""
InventoryReservation }|--|| Cart: ""
InventoryReservation }|--|| Order: ""
InventoryReservation }|--|| Product: ""
User ||--|| Token: ""
User }|--|{ Group: ""
User }|--|{ Permission: ""
