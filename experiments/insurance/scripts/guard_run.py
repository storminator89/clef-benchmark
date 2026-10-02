"""RAM guard only; does not change system settings or shared runtime."""
import subprocess,sys,time,json,psutil,datetime,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--log',type=Path,required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();assert a.command
child=subprocess.Popen(a.command)
with a.log.open('x') as f:
 while child.poll() is None:
  try:
   proc=psutil.Process(child.pid);rss=proc.memory_info().rss+sum(c.memory_info().rss for c in proc.children(recursive=True));avail=psutil.virtual_memory().available
   row={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':child.pid,'rss_bytes':rss,'available_bytes':avail}
   if rss>8.3*1024**3 or avail<0.4*1024**3:
    row['event']='memory_guard_stop';f.write(json.dumps(row)+'\n');f.flush();child.terminate()
    try:child.wait(timeout=15)
    except subprocess.TimeoutExpired:child.kill()
    raise SystemExit('Stopped to protect RAM; consult resource monitor')
   f.write(json.dumps(row)+'\n');f.flush()
  except psutil.NoSuchProcess:pass
  time.sleep(2)
raise SystemExit(child.returncode)
