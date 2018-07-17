mk needed swap:
  cmd.run:
   - name: dd if=/dev/zero of=/swapfile bs=1024k count=1000

mk it swap:
  cmd.run:
   - name:  mkswap /swapfile

switch on swap:
  cmd.run:
   - name: swapon /swapfile

git:
  pkg.installed

nodejs:
  pkg.installed

ruby-dev:
  pkg.installed

ruby-build:
  pkg.installed

libpq-dev:
  pkg.installed

rbenv:
  pkg.installed

ruby:
  pkg.installed

rake:
  pkg.installed

nginx:
  pkg.installed: []
  service.running:
    - require:
      - pkg: nginx

install bundler:
  cmd.run:
   - name: gem install bundler

install nokogiri:
  cmd.run:
   - name: gem install nokogiri -v 1.6.7.2
   - user: www-data
   - group: www-data

install unicorn:
  cmd.run:
   - name: gem install unicorn

install foreman:
  cmd.run:
   - name: gem install foreman

/etc/nginx/sites-enabled/default:
  file.managed:
   - source: salt://devops-skill-challenge/nginx.config

/var/www:
  file.directory:
   - user: www-data
   - group: www-data
   - mode: 755

deploy code:
  cmd.run:
   - name: git clone https://github.com/navsmb/devops-skill-challenge
   - cwd: /var/www
   - user: www-data
   - group: www-data
   - require:
     - pkg: git

install gems:
  cmd.run:
   - name: bundle install
   - cwd: /var/www/devops-skill-challenge

fix secrets:
  file.managed:
   - name: /var/www/devops-skill-challenge/config/secrets.yml
   - source: salt://devops-skill-challenge/secrets.yml
   - user: www-data
   - group: www-data

migrate:
  cmd.run:
   - name: rake db:migrate RAILS_ENV=development
   - cwd: /var/www/devops-skill-challenge

start app:
  cmd.run:
   - name: foreman start
   - cwd: /var/www/devops-skill-challenge

restart nginx:
  cmd.run:
   - name: service nginx restart
