from fabric.api import local, run, sudo, cd
from fabric.api import env
from fabric.contrib import files
import config

env.hosts = config.HOSTS
# centos 7
def install_packages_centos_7():
    packages = [
        'python3-pip',
        'python3-devel',
        'python3-venv',
        'nginx',
        'git-core'
    ]
    sudo('yum install -y {}'.format(' '.join(packages)))


def create_venv():
    if files.exists(config.VENV_PATH):
        run(f"rm -rf {config.VENV_PATH}")
    run('python3 -m venv venv')

def install_project_code():
    if not files.exists(config.PROJECT_PATH):
        run(f'git clone {config.PROJECT_GIT_PATH}')
    else:
        with cd(config.PROJECT_PATH):
            run('git pull')
    
def install_pip_requirements():
    with cd(config.PROJECT_PATH):
        run(f'{config.VENV_PATH}/bin/pip install -r requirements.txt -U')

def configure_uwsgi():
    sudo("python3 -m pip install uwsgi")
    sudo("mkdir -p /etc/uwsgi/sites")
    files.upload_template('templates/uwsgi.ini', '/etc/uwsgi/sites/gqlshop.ini', use_sudo=True)
    files.upload_template('templates/uwsgi.service', '/etc/systemd/system/uwsgi.service', use_sudo=True)

def configure_nginx():
    if files.exists("/etc/nginx/sites-enabled/default"):
        sudo("rm /etc/nginx/sites-enabled/default")
    files.upload_template('templates/nginx.conf', '/etc/nginx/sites-enable/gqlshop.conf', use_sudo=True)

def migrate_database():
    with cd(config.PROJECT_PATH):
        run(f'{config.VENV_PATH}/bon/python manage.py migrate')

def restart_all():
    sudo("systemctl daemon-reload")
    sudo("systemctl reload nginx")
    sudo("systemctl restart uwsgi")




def bootstrap():
    install_packages_centos_7()
    create_venv()
    install_project_code()
    install_pip_requirements()
    configure_uwsgi()
    configure_nginx()
    migrate_database()
    restart_all()


# def hello():
#     sudo('whoami')