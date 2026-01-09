<script lang="ts">
  import '../app.css';
</script>

<svelte:head>
  <meta charset="utf-8" />
  <link rel="icon" href="%sveltekit.assets%/favicon.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />

  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <!-- Font Awesome -->
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</svelte:head>

<div class="min-vh-100 bg-light">
  <!-- Navigation -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold" href="/">
        <i class="fas fa-clipboard-check me-2"></i>
        M0>.... &*M$0 $*>8#@
      </a>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">
              <i class="fas fa-tachometer-alt me-1"></i>!E6,K0M!
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/inspect">
              <i class="fas fa-plus me-1"></i>(5@( $*>8#@
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/compliance">
              <i class="fas fa-check-circle me-1"></i>(A*>2(
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/reports">
              <i class="fas fa-chart-bar me-1"></i>95>2
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <main class="flex-grow-1">
    <slot />
  </main>

  <!-- Footer -->
  <footer class="bg-white border-top py-3 mt-5">
    <div class="container-fluid">
      <div class="row">
        <div class="col-12 text-center">
          <small class="text-muted">
            M0>. .98B2 '?>0@ &*M$0 $*>8#@ *M0#>2@ &copy; 2024
          </small>
        </div>
      </div>
    </div>
  </footer>
</div>

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>