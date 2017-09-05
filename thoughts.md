I recently came across a pretty interesting Cloud Foundry project called the
multi-buildpack.  Basically this is a buildpack that allows you to use more
than one buildpack for your application.  This can be great if you application
has need of more than one language or if you are interested in fronting your
application with nginx and the staticfile buildpack.  I was most interested in
fronting some Python applications with nginx to take advantage of some of
things like easy and cheap WAF capabilities and serving static content from
nginx rather than my python application.

For the TL;DR crowd --  
The multi-buildpack -- https://github.com/cloudfoundry-incubator/multi-buildpack  
My example app -- https://github.com/epoelke/multibuildpack-test-app

The first thing that changes is that in your manifest you have a reference to
the multi-buildpack instead of the individual buildpacks.  So you have this in
your manifest --
```
buildpack: https://github.com/cloudfoundry-incubator/multi-buildpack
```
You will also need to create a new yaml file that the multi-buildpack will use
to inform it of all the buildpacks your application needs to use.  It should be
called **multi-buildpack.yml** and should look something like this --
```
buildpacks:
  - https://github.com/cloudfoundry/python-buildpack
  - https://github.com/cloudfoundry/staticfile-buildpack
```
The first thing that you should know here is that you _must_ use buildpacks
from github for all buildpacks.  You cannot use the buildpacks that are shipped
with Cloud Foundry.  The second thing you should know is that order here does
matter.  The last buildpack in the list will be your "main" buildpack.  Meaning
that the behavior of that buildpack for things like built in startup commands
or anything else will be the behavior you should expect.  In my case the
behavior of the staticfile buildpack is what happened.

When using the staticfile buildpack just to get nginx you should always push in
a custom nginx.conf file as part of your application to avoid any accidental
configuration mishaps.  You can see the example nginx.conf in the
multibuildpack-test-app github repo.  The configuration I used has some rate
limiting added for all endpoints other than **/nginx**.  The location for
**/nginx** just returns a 200 without ever reaching my Python application.  In
a real application you would probably configure a couple of locations that
would serve static content instead of just returning a 200.

My Python application is configured to listen on a unix socket instead of an IP
address and nginx actually proxies requests to the unix socket.  This approach
has a bit less overhead by eliminating TCP and we want to be as optimized as
possible running inside a container.  So you can see the proxypass directive in
the nginx.conf file points to a unix socket instead of an IP.  Its also
important to set the server directive to `_`.  This will cause nginx to accept
requests for any hostname it receives and makes your configuration nice and
templated.  You can also force HTTPS connections only to nginx endpoints by
setting the environment variable of `FORCE_HTTPS: true`.  This will _only_
apply to nginx endpoints that are not proxypass'd.  You will still need to
force https at the application layer for your non-nginx endpoints.

Another thing that is suboptimal here is choosing a health check strategy.
  There are three options in Cloud Foundry: PORT, PROCESS, and HTTP.  Using
PORT here is not a great idea.  If the application that you are proxying to is
dead, nginx will still respond to connections to the port and the application
will be seen as "healthy" by Cloud Foundry.  Process is also a bad option here
since we are starting multiple processes.  All the processes would need to die
for the application be be seen as unhealthy.  So that leaves us with HTTP as
the best option.  The HTTP health check will by default perform an HTTP GET on
/ and if it receives a 200 then it is seen as healthy.  The default behavior
may have the same problem as the PORT strategy.  But the HTTP endpoint also
allows you to provide a custom endpoint for health checking.  This nicely
solves health checking for both nginx and our application.  So I implemented a
/healthcheck endpoint in the Python application which effectively checks both
nginx and the application.

The last thing that needed to be customized was the start command for the
application.  In my case I needed to start both the Python application (running
in uwsgi application server) and nginx.  Since the last buildpack in my
multi-buildpack.yml file is staticfile the startup behavior is that of the
staticfile buildpack.  It has a built-in startup command (boot.sh) so one is
not typically provided when using this buildpack.  But since I needed to start
my Python process first we needed to provide one and then invoke the nginx
startup after.  So my startup command launches my uwsgi application server,
 backgrounds the process, then runs the nginx startup script last.
```
command: uwsgi --master --processes 4 --threads 2 --http /tmp/uwsgi.sock --wsgi-file public/app.py & ./boot.sh
```
Overall this is a great new capability for buildpacks.  It's important to note
this project is still in the incubator so it may change before it sees a 1.0
release.




