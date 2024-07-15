set -e

function cleanup() {
  docker stop hayato
  docker container rm --force hayato
  echo "cleanup complete"
}

trap cleanup EXIT

docker build --tag hayato:dev .
docker run --rm --name hayato -v ./.env:/app/.env -v ./out:/app/out localhost/hayato:dev
