--
Question:
For each user, show:
their total number of bookings,
their total confirmed bookings,
their total amount spent on confirmed bookings,
and their confirmation rate (confirmed ÷ total).
Use a CTE.


WITH user_stats AS (
  SELECT
      u.user_id,
      u.name,
      COUNT(*) AS total_bookings,
      SUM(CASE WHEN b.status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings,
      SUM(CASE WHEN b.status = 'confirmed' THEN b.amount ELSE 0 END) AS confirmed_spend
  FROM users u
  JOIN bookings b ON b.user_id = u.user_id
  GROUP BY u.user_id, u.name
)
SELECT
  user_id,
  name,
  total_bookings,
  confirmed_bookings,
  confirmed_spend,
  (confirmed_bookings/ total_bookings) AS confirmation_rate
FROM user_stats
ORDER BY user_id;

--
Find the top 2 users who have spent the most money on confirmed bookings.
For each of these users, show:

user_id
name
total_confirmed_bookings
total_amount_spent


with user_stats as (
	select  u.user_id , u.name ,
	count(1) as total_confirmed_bookings,
	sum(b.amount) as total_amount_spent
	from users u inner join  bookings b on u.user_id = b.user_id
	where b.status='confirmed'
	group by u.user_id , u.name 
	order by total_amount_spent desc
)

select * from
(
	select rank() over(order by total_amount_spent desc) as top_spenders, * from user_stats
)
where top_spenders <= 2