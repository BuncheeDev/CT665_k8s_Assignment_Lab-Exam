# CT665 Kubernetes Lab Exam (`www.iam-712.com` & `admin.iam-712.com`)

* **ผู้จัดทำ:** นายมงคล เพชรแสวง (Mr. Mongkol Petsawang)
* **รหัสนักศึกษา:** `68130712` (`xxx = 712`)
* **โครงสร้างคลัสเตอร์:** Kubernetes 3 Nodes (`minikube`, `minikube-m02`, `minikube-m03`) พร้อม Flannel CNI และ NGINX Ingress Controller

## บริการทั้งหมด (Deployments & Ingress Routing)

| URL | Deployment | Service | หน้าที่ |
|---|---|---|---|
| `http://www.iam-712.com/` (และ `www.id-712.com`) | `portal-712` | `portal-712:80` | แสดงรูปภาพ ชื่อ และรหัสนักศึกษา |
| `http://www.iam-712.com/research` | `app-research` | `app-research:80` | แสดงสรุปงานวิจัย Neural of Law (300–500 คำ) |
| `http://www.iam-712.com/api-712/<ข้อความ>` | `api-712` | `api-712:80` | แสดงข้อความ `<ข้อความ>` ขนาดใหญ่กลางหน้าจอ |
| `http://admin.iam-712.com/` | `admin-712` | `admin-712:80` | หน้าปุ่มเลือกแก้ไขข้อมูล `portal` และ `research` ผ่าน ConfigMap |
| `http://www.iam-712.com/arch` | `portal-712` | `portal-712:80` | แผนภาพโครงสร้างระบบแบบโต้ตอบ (Archify) |

## ขั้นตอนการ Deploy

```bash
# 1. สร้างคลัสเตอร์ Kubernetes 3 Nodes
minikube start --driver=docker --nodes=3 --cni=flannel --memory=1800mb --cpus=2 --force

# 2. รันสคริปต์ Deploy อัตโนมัติ
chmod +x deploy.sh
./deploy.sh
```
