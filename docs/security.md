### Security

[http://blog.al4.co.nz/2011/05/setting-up-a-secure-ubuntu-lamp-server/](http://blog.al4.co.nz/2011/05/setting-up-a-secure-ubuntu-lamp-server/)

**Install ufw**

ufw: uncomplicated firewall, is a great little firewall program that you can use to control your server access rules. The default set below are fairly standard for a web server but are quite permissive. You may want to only allow connection on a certain ip if you will always be accessing your pi from a fixed ip.

UFW Documentation
[https://help.ubuntu.com/community/UFW](https://help.ubuntu.com/community/UFW)

    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 22/tcp
    sudo ufw enable

**Change root password**

Set root password

    sudo passwd root

The default root password used in the ready to go image is **raspberry**. 
Change this to a hard to guess password to make your root account secure.

**Secure MySQL**

Run mysql_secure_installation see [mysql docs](http://dev.mysql.com/doc/refman/5.0/en/mysql-secure-installation.html)

    mysql_secure_installation

**Secure SSH**

Disable root login:

    sudo nano /etc/ssh/sshd_config

Set **PermitRootLogin** to **no**
