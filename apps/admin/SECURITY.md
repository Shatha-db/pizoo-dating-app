alter table services enable row level security;
alter table posts enable row level security;

-- اسمِّح بالقراءة للجميع (الموقع العام)
create policy "public read services" on services for select using (true);
create policy "public read posts" on posts for select using (true);

-- اسمِّح بكتابة/تعديل/حذف فقط لإيميل الإدارة
-- بدِّل الإيميل أدناه بإيميل الإدارة الحقيقي (مثلاً info@shatha.ch)
create policy "admin write services" on services
for all using (auth.jwt() ->> 'email' = 'info@shatha.ch')
with check (auth.jwt() ->> 'email' = 'info@shatha.ch');

create policy "admin write posts" on posts
for all using (auth.jwt() ->> 'email' = 'info@shatha.ch')
with check (auth.jwt() ->> 'email' = 'info@shatha.ch');
