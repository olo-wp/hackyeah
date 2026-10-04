# Deploy RouteAble na GCP VM

Workflow `.github/workflows/deploy-gcp.yml` buduje API, MCP i web na GitHubie,
przesyła obrazy przez SSH jako `ubuntu@34.118.126.240` i uruchamia produkcyjny Compose.
Logowanie używa hasła z sekretu `GCP_SSH_PASSWORD` przez `sshpass -e`.
Startuje przy pushu na `main` lub ręcznie przez Actions → Deploy to GCP VM.
Obrazy są oznaczone SHA commita. Nie potrzeba rejestru obrazów ani konta usługi GCP.
Konfiguracja zakłada Linux x86_64, SSH na porcie 22 oraz Docker Engine z Compose v2
obsługującym `up --wait`. Dla ARM zmień `platforms` w trzech krokach buildu.

## Jednorazowa konfiguracja maszyny

1. Zainstaluj Docker Engine i wtyczkę Compose według instrukcji dla systemu VM:
   https://docs.docker.com/engine/install/. Użytkownik SSH musi móc uruchamiać
   `docker info` i `docker compose version` bez sudo. Przy dodaniu do grupy
   `docker` zaloguj się ponownie. Grupa Docker daje uprawnienia administracyjne.
2. Konto `ubuntu` musi istnieć na VM i mieć ustawione hasło odpowiadające
   sekretowi `GCP_SSH_PASSWORD`. W zaufanej konsoli ustaw je interaktywnie:
   `sudo passwd ubuntu`. Serwer SSH musi zezwalać temu kontu na logowanie
   hasłem (`PasswordAuthentication yes` w efektywnej konfiguracji sshd).
   Workflow nie tworzy konta ani nie zmienia ustawień SSH na VM.
3. Ustaw rekordy DNS **A**:

   | Nazwa | Wartość |
   | --- | --- |
   | `routeable.net` | `34.118.126.240` |
   | `api.routeable.net` | `34.118.126.240` |

   Zarezerwuj ten adres jako statyczny w GCP. Rekordy AAAA ustawiaj tylko przy
   działającym IPv6 na tej VM. Przed pierwszym wdrożeniem obie domeny muszą
   wskazywać na maszynę.
4. W firewallu GCP i systemu otwórz TCP 80/443; opcjonalnie UDP 443 dla HTTP/3.
   Zapewnij dostęp runnera GitHub do SSH TCP 22 oraz wyjście VM do internetu i bazy.
   Porty API/web nie są publikowane na hoście. MCP słucha tylko na localhost:3002.
   Porty 80/443 muszą być wolne od innego reverse proxy.
5. Na VM jako użytkownik `ubuntu`:

   ```bash
   mkdir -p ~/routeable
   chmod 700 ~/routeable
   # Wklej zawartość deploy/.env.example, potem uzupełnij dane:
   nano ~/routeable/.env
   chmod 600 ~/routeable/.env
   ```

   Ustaw prawdziwy `DATABASE_URL`, `GEMINI_API_KEY` i `ORS_API_KEY`.
   API wykona migracje przed startem; konto bazy potrzebuje uprawnień do tabel
   i indeksów. Firewall bazy powinien dopuszczać VM. Nie kopiuj `.env` do Git.

## GitHub → Settings → Environments → production

Dodaj sekrety środowiska:

| Sekret | Zawartość |
| --- | --- |
| `GCP_SSH_PASSWORD` | Hasło konta `ubuntu` ustawione na VM |
| `GCP_SSH_KNOWN_HOSTS` | Zweryfikowany wpis known_hosts dla `34.118.126.240` |

Klucz hosta odczytaj w zaufanej konsoli VM:

```bash
sudo cat /etc/ssh/ssh_host_ed25519_key.pub
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Sekret known_hosts ma format `34.118.126.240 ssh-ed25519 AAAA...` — użyj
algorytmu i klucza odczytanego z VM. Workflow wymaga ścisłej weryfikacji hosta.
Dodaj też **zmienną** środowiska `NEXT_PUBLIC_MAPTILER_KEY`. To publiczny klucz
osadzany podczas buildu; ogranicz jego origin do `https://routeable.net`.
Po jego zmianie uruchom workflow ponownie.

## Reverse proxy i HTTPS

`deploy/Caddyfile` kieruje `routeable.net` → `web:3000` i
`api.routeable.net` → `api:3001`, zachowując ścieżki API (np. `/api/places/search`).
Caddy automatycznie uzyskuje i odnawia certyfikaty oraz przekierowuje HTTP na HTTPS.
Certyfikaty pozostają w wolumenie `routeable_caddy_data` pomiędzy wdrożeniami.
Web komunikuje się z API również wewnątrz sieci Docker, a CORS API dopuszcza
`https://routeable.net`.

Dokumentacja: [Caddy reverse_proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy),
[Automatic HTTPS](https://caddyserver.com/docs/automatic-https),
[GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

## Weryfikacja i obsługa

Po wdrożeniu workflow czeka na zdrowe kontenery i sprawdza oba adresy HTTPS:

```bash
curl -f https://api.routeable.net/health
curl -I https://routeable.net
```

Na VM:

```bash
cd -P ~/routeable/current
export RELEASE="$(basename "$PWD")"
export ROUTEABLE_ENV_FILE="$HOME/routeable/.env"
docker compose --env-file "$ROUTEABLE_ENV_FILE" -f compose.yml ps
docker compose --env-file "$ROUTEABLE_ENV_FILE" -f compose.yml logs --tail 100
```

Jeżeli wdrożenie nie przejdzie, workflow zgłasza błąd; `current` wskazuje ostatnie
udane wydanie. Aktualizacja może spowodować krótką przerwę. Nie ma automatycznego
rollbacku bazy ani kontenerów. Nie usuwaj wolumenów Caddy (`down -v`).
Archiwum obrazów jest usuwane po udanym wdrożeniu; starsze obrazy i katalogi
wydań pozostają do ręcznego usunięcia, więc monitoruj wolne miejsce.

Przywrócenie poprzednich obrazów (bez cofania migracji):

```bash
previous_sha=TU_SHA_POPRZEDNIEGO_WYDANIA
cd "$HOME/routeable/releases/$previous_sha"
export RELEASE="$previous_sha"
export ROUTEABLE_ENV_FILE="$HOME/routeable/.env"
docker compose --env-file "$ROUTEABLE_ENV_FILE" -f compose.yml up -d --no-build --wait
docker compose --env-file "$ROUTEABLE_ENV_FILE" -f compose.yml up -d --no-deps --force-recreate caddy
curl -f https://api.routeable.net/health
curl -f -o /dev/null https://routeable.net
ln -sfn "$PWD" "$HOME/routeable/current"
```

Przed rollbackiem upewnij się, że poprzednia aplikacja jest zgodna z bieżącym
schematem bazy. MCP można udostępnić lokalnie przez tunel:
`ssh -L 3002:127.0.0.1:3002 ubuntu@34.118.126.240`.
