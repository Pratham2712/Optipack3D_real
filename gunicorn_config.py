# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 3
# accesslog = "/home/ec2-user/Optipack3D_real/gunicorn/access.log"
# errorlog = "/home/ec2-user/Optipack3D_real/gunicorn/error.log"
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = "debug"
