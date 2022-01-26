# Run with:
#
# ruby [filename of this script]

# Given a site that is backed by a Kubernetes deployment,
# monitor the site for HTTP bad status while scaling the deployment up and down.

# Before using this script:
#
#   - Make sure kubectl context is correctly set. It probably should be staging which is where you most likely want to test on.
#   - Make sure DEPLOYMENT (below) is set to the correct deployment name.
#   - Disable any autoscaler tied to the deployment, because that might interfere with your manual scaling.
#     For example, if you want to test on force-web deployment, run:
#       kubectl edit HorizontalPodAutoscaler force-web
#     When the config pops up, go to the line that says monitor <k8s-deployment-name> deployment, change it to some bogus deployment such as 'foobar'.
#     Revert the config when done with testing.
#
# Tune the script to your needs by:
#
#   - Changing pod count.
#   - Adding commands useful to monitor status of pods or site.
#   - Set the URL of the site that is to be monitored.

DEPLOYMENT = <k8s-deployment-name>
SITEURL = <staging-site-url>

# Scale Staging Force deployment pods to specific count.
def scaleDeployment(count)
  time = Time.new
  puts "----------#{time}----------"
  puts "Scaling #{DEPLOYMENT} deployment to #{count} pods."
  cmd = "kubectl scale --replicas=#{count} deployment/#{DEPLOYMENT}"
  output = %x( #{cmd} )
  puts output
end

# Check HTTP status of site.
def checkHTTPstatus()
  time = Time.new
  puts "----------#{time}----------"

  checkHTTPCmd = "wget -S -qO /dev/null '#{SITEURL}' 2>&1 | grep HTTP"
  getPodsCmd = "kubectl get pods | grep #{DEPLOYMENT}"
  # how to filter out old replica sets from the output?
  getReplicaSetCmd = "kubectl get rs | grep #{DEPLOYMENT}" 
  getRolloutStatusCmd = "kubectl rollout status deployment #{DEPLOYMENT}"
  getDeploymentCmd = "kubectl get deployment | grep #{DEPLOYMENT}"
  getEndpointsCmd = "kubectl get endpoints #{DEPLOYMENT} -o yaml | grep 'name: #{DEPLOYMENT}-'"

  puts "HTTP status:"
  system(checkHTTPCmd)
  puts "pod endpoints list:"
  system(getEndpointsCmd)
  puts "deployment status:"
  system(getDeploymentCmd)
end

# Run checkHTTPstatus a bunch times with a half second pause in between.
def observeHTTPstatus(count)
  while (count > 0)
    checkHTTPstatus()
    count -= 1
    sleep 0.5
  end
end

observeHTTPstatus(5)
scaleDeployment(7)
observeHTTPstatus(30)
scaleDeployment(1)
observeHTTPstatus(30)
