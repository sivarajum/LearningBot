# GCP Networking: LB Options
- External HTTP(S) LB: global, Layer7.
- Internal HTTP(S)/TCP: inside VPC.
- PSC/Private Service Connect for private access to services.
- Decision: internet ingress -> ext HTTP(S); internal microservices -> internal; need private SaaS -> PSC.
