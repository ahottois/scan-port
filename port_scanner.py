#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import argparse
from datetime import datetime

def get_listening_ports():
    """Récupère la liste des ports en écoute sur le système."""
    try:
        # Exécute la commande ss pour obtenir les ports en écoute
        cmd = ["ss", "-tuln"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de ss -tuln: {e}")
        return ""

def get_established_connections():
    """Récupère la liste des connexions établies sur le système."""
    try:
        # Exécute la commande ss pour obtenir les connexions établies
        cmd = ["ss", "-tun", "state", "established"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de ss -tun state established: {e}")
        return ""

def get_process_for_port(port, protocol="tcp"):
    """Récupère le processus associé à un port spécifique."""
    try:
        if protocol.lower() == "tcp":
            proto_arg = "TCP"
        else:
            proto_arg = "UDP"
            
        cmd = ["sudo", "lsof", "-i", f"{proto_arg}:{port}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de lsof -i {proto_arg}:{port}: {e}")
        return ""

def parse_listening_ports(output):
    """Parse la sortie de ss -tuln pour extraire les ports en écoute."""
    listening_ports = []
    lines = output.strip().split('\n')
    
    # Ignorer la première ligne d'en-tête
    if len(lines) > 1:
        lines = lines[1:]
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 5:
            protocol = parts[0].lower()
            local_addr = parts[4]
            
            # Extraction du port
            if ':' in local_addr:
                ip, port = local_addr.rsplit(':', 1)
                listening_ports.append({
                    'protocol': protocol,
                    'local_address': ip,
                    'port': port
                })
    
    return listening_ports

def parse_established_connections(output):
    """Parse la sortie de ss pour extraire les connexions établies."""
    established_conns = []
    lines = output.strip().split('\n')
    
    # Ignorer la première ligne d'en-tête
    if len(lines) > 1:
        lines = lines[1:]
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 5:
            protocol = parts[0].lower()
            local_addr = parts[3]
            remote_addr = parts[4]
            
            # Extraction des adresses et ports
            if ':' in local_addr and ':' in remote_addr:
                local_ip, local_port = local_addr.rsplit(':', 1)
                remote_ip, remote_port = remote_addr.rsplit(':', 1)
                
                established_conns.append({
                    'protocol': protocol,
                    'local_address': local_ip,
                    'local_port': local_port,
                    'remote_address': remote_ip,
                    'remote_port': remote_port
                })
    
    return established_conns

def parse_process_info(output):
    """Parse la sortie de lsof pour extraire les informations de processus."""
    processes = []
    lines = output.strip().split('\n')
    
    # Ignorer la première ligne d'en-tête
    if len(lines) > 1:
        lines = lines[1:]
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 9:
            process = {
                'command': parts[0],
                'pid': parts[1],
                'user': parts[2],
                'fd': parts[3],
                'type': parts[4],
                'device': parts[5],
                'protocol': parts[7],
                'address': parts[8]
            }
            processes.append(process)
    
    return processes

def main():
    parser = argparse.ArgumentParser(description='Vérifier les ports ouverts et les connexions sous Linux.')
    parser.add_argument('-l', '--listening', action='store_true', 
                        help='Afficher uniquement les ports en écoute')
    parser.add_argument('-c', '--connections', action='store_true', 
                        help='Afficher uniquement les connexions établies')
    parser.add_argument('-p', '--processes', action='store_true', 
                        help='Inclure les informations sur les processus (nécessite sudo)')
    parser.add_argument('-o', '--output', type=str, 
                        help='Sauvegarder les résultats dans un fichier')
    
    args = parser.parse_args()
    
    # Si aucune option n'est spécifiée, afficher tout
    if not (args.listening or args.connections):
        args.listening = True
        args.connections = True
    
    results = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results.append(f"Scan des ports et connexions - {now}\n")
    results.append("="*50 + "\n")
    
    # Récupérer et analyser les ports en écoute
    if args.listening:
        listening_output = get_listening_ports()
        listening_ports = parse_listening_ports(listening_output)
        
        results.append("\nPorts en écoute:\n")
        results.append("-"*50 + "\n")
        results.append(f"{'Protocole':<10} {'Adresse locale':<20} {'Port':<10}")
        results.append("-"*50 + "\n")
        
        for port_info in sorted(listening_ports, key=lambda x: int(x['port'])):
            results.append(f"{port_info['protocol']:<10} {port_info['local_address']:<20} {port_info['port']:<10}")
            
            # Ajouter les informations de processus si demandé
            if args.processes:
                process_output = get_process_for_port(port_info['port'], port_info['protocol'])
                processes = parse_process_info(process_output)
                
                if processes:
                    for proc in processes:
                        results.append(f"  └─ {proc['command']} (PID: {proc['pid']}, User: {proc['user']})")
    
    # Récupérer et analyser les connexions établies
    if args.connections:
        established_output = get_established_connections()
        established_conns = parse_established_connections(established_output)
        
        results.append("\nConnexions établies:\n")
        results.append("-"*80 + "\n")
        results.append(f"{'Protocole':<10} {'Adresse locale':<20} {'Port local':<10} {'Adresse distante':<20} {'Port distant':<10}")
        results.append("-"*80 + "\n")
        
        for conn in sorted(established_conns, key=lambda x: int(x['local_port'])):
            results.append(
                f"{conn['protocol']:<10} "
                f"{conn['local_address']:<20} "
                f"{conn['local_port']:<10} "
                f"{conn['remote_address']:<20} "
                f"{conn['remote_port']:<10}"
            )
    
    # Afficher les résultats
    output_text = "\n".join(results)
    print(output_text)
    
    # Sauvegarder dans un fichier si demandé
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"\nLes résultats ont été sauvegardés dans {args.output}")

if __name__ == "__main__":
    main()
