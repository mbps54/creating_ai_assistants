# Network Administrator Wiki — LLC “IntegraLabs”

The document contains the main rules and templates for configuring the company's network equipment and services.

---

## 🔌 User Port Configuration Template (Cisco Access Port)

```
interface GigabitEthernet1/0/24
 description Workplace connection (HR-WS-204)
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 storm-control broadcast level 5.00
 no shutdown
```

> VLAN 20 — the working VLAN for office employees.
> Portfast and BPDU Guard are enabled by default on all access ports.

---

## 🖨️ Port Configuration Template for a Network Printer (Cisco)

```
interface GigabitEthernet1/0/10
 description Network printer HP LJ4050 (printroom-1)
 switchport mode access
 switchport access vlan 40
 spanning-tree portfast
 storm-control broadcast level 2.00
 no cdp enable
 no shutdown
```

> VLAN 40 — printer VLAN, isolated from user segments by ACL rules.
> CDP is disabled for improved security.

---

## 📡 Wi-Fi Settings

Wi-Fi in the office is divided into 3 SSIDs:

- **Integralabs-Corp**
  - For employees only
  - Authentication via 802.1x (Active Directory)
  - VLAN 20
- **Integralabs-Guest**
  - For temporary visitors
  - Authorization via captive portal
  - VLAN 100, NAT, speed limit 10 Mbps
- **Integralabs-IoT**
  - For network devices (TVs, projectors, cameras)
  - WPA2-PSK, separate VLAN 70, internet access without LAN access

> Controller: Cisco WLC 9800, firmware 17.9.3
> Guest SSID password rotation — monthly, via helpdesk request.

---

## 🧱 Basic ACL Rules for User VLAN (vlan 20)

```
ip access-list extended USER-ACCESS
 permit ip any 10.10.0.0 0.0.255.255
 deny ip any 10.99.0.0 0.0.255.255
 deny ip any 172.16.0.0 0.15.255.255
 permit ip any any
```

> VLAN 20 has limited access to the DMZ and is fully isolated from the service VLAN.

---

## 🔁 IP Address Reservation Rules

- All network devices receive IP via DHCP with MAC-based reservation.
- Ranges:
  - VLAN 20: 10.10.20.100–199 (workstations)
  - VLAN 40: 10.10.40.10–99 (printers)
  - VLAN 70: 10.10.70.50–200 (IoT)
- All static reservations are made through the `dhcp_static.cfg` file stored in Git (`/infra/net/dhcp/`).

---

## 🔄 Maintenance Schedule

- Switch firmware update — every second Thursday of the month
- Configuration integrity check — every Friday at 16:00 (comparison with Git)
- Planned Wi-Fi AP reboot — first Sunday of the month at 6:00

---

## Contacts

- Senior Network Engineer: `@alex_netadmin`
- Operations Department: `netops@integralabs.ru`
- Configuration Git Repository: `git.integralabs.local/net-configs`

# Servers and Services in the Infrastructure

## Accounting Server
- Purpose: storage of accounting documents, 1C
- IP: 10.1.1.15
- Hostname: accounting.local

## Accounting Switches
- asw2

## BI Analytics Server
- Purpose: reporting, visualization, Power BI Gateway
- IP: 10.1.2.10
- Hostname: bi-gateway.local

## File Server
- Purpose: shared file access for employees
- IP: 10.1.1.30
- Hostname: files.local

## Mail Server
- Purpose: corporate email, SMTP/IMAP
- IP: 10.1.2.25
- Hostname: mail.local

## Domain Name Server
- Purpose: user authentication
- IP: 8.8.4.4
