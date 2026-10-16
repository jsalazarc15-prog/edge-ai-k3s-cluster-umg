# Clúster de Edge Computing para Inferencia de IA Local Autónoma (Air-Gapped)

**Universidad Mariano Gálvez de Guatemala**  
**Facultad de Ingeniería en Sistemas de Información y Ciencias de la Computación**  
**Curso:** Arquitectura de Sistemas II (Sección C)  
**Autores:** 
Javier Adolfo Salazar Carías — **Carné:** 0900-22-1009  
Luis David Cerna Culajay — **Carné:** 0900-23-19226 
---

## Descripción de la Arquitectura
Infraestructura física de **Edge Computing 100% aislada de internet (Air-Gapped)**, orquestada con Kubernetes ligero (**K3s**) sobre nodos x86 de bajo consumo para ejecutar un asistente de Inteligencia Artificial autónomo (**Caso 3: Procesamiento de Lenguaje para Asistencia Local**).

Su núcleo ejecuta el Modelo de Lenguaje Pequeño (**SLM**) **`Qwen2:0.5b`** cuantizado a 4 bits (`GGUF Q4_0`), procesando consultas en tiempo real sin conexión a la nube pública, garantizando soberanía de datos y latencias inferiores a **800 ms**.

### Características Principales (Infraestructura como Código - IaC)
* **Alta Disponibilidad (HA) y Resiliencia:** Configuración de reglas topológicas `nodeAffinity` (preferencia hacia el Worker Lenovo de 16 núcleos) y `podAntiAffinity` combinadas con **Horizontal Pod Autoscaler (HPA)** al 80% de CPU para conmutación por error (*Failover*) automática hacia el nodo Maestro Huawei.
* **Persistencia Física Nativa (`hostPath`):** Anclaje directo a los discos locales (`/opt/ollama-data` y `/opt/grafana-data`) para inmunidad total ante apagones eléctricos sin requerir descargas externas.
* **Observabilidad y QoS:** Monitoreo en tiempo real a nivel de kernel mediante **Prometheus Node Exporter** (`hostNetwork`) y visualización analítica en **Grafana**.
* **Seguridad Perimetral y Cumplimiento Legal (SIT Guatemala):** Red privada Clase C (`192.168.1.0/24`) en Dual Stack (IPv4/IPv6) gobernada por **pfSense** con Portal Cautivo local, operando en bandas de uso libre ISM (Decreto 94-96, Ley General de Telecomunicaciones).

---

## Topología Física y Lógica del Clúster

| Nodo / Equipo | Dirección IP | Rol en Arquitectura | Especificaciones Clave |
| :--- | :--- | :--- | :--- |
| **Firewall pfSense** | `192.168.1.1/24` | Gateway L3 / Portal Cautivo | Dual Stack IPv4/IPv6, Bloqueo total WAN (`Air-Gap`). |
| **Master Node (Huawei)** | `192.168.1.72/24` | Control Plane + Nodo Failover | K3s Server, FastAPI Web (`:31683`), Grafana (`:31250`), Prometheus. |
| **Worker Node (Lenovo)** | `192.168.1.71/24` | Motor de Inferencia IA Primario | 16 Núcleos Lógicos CPU (`requests=4`, `limits=14`), Ollama (`Qwen2:0.5b`). |

---

## Estructura del Repositorio
* `/k8s-manifests/`: Manifiestos declarativos YAML de Kubernetes (Deployments, Services, HPA, afinidad de nodos y volúmenes `hostPath`).
* `/ollama-model/`: Definición del `Modelfile` para la compilación offline del binario cuantizado `qwen2.gguf`.
* `/fastapi-web/`: Servidor web asíncrono e interfaz gráfica oscura para interacción con el Asistente Edge AI en la LAN.
