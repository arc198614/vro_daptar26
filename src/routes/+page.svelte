<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  let inspections: any[] = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      const response = await fetch('/api/inspections');
      const data = await response.json();

      if (data.success) {
        inspections = data.inspections;
      } else {
        error = data.error || 'Failed to load inspections';
      }
    } catch (err) {
      error = 'Failed to load inspections';
      console.error('Error loading inspections:', err);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>!E6,K0M! - M0>.... &*M$0 $*>8#@</title>
</svelte:head>

<div class="container-fluid py-4">
  <div class="row">
    <div class="col-12">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0">!E6,K0M! - M0>.... &*M$0 $*>8#@</h1>
        <a href="/inspect" class="btn btn-primary">
          <i class="fas fa-plus me-2"></i>(5@( $*>8#@
        </a>
      </div>

      {#if loading}
        <div class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3">$*>8#M/> 2K! 9K$ 9G$...</p>
        </div>
      {:else if error}
        <div class="alert alert-danger" role="alert">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {error}
        </div>
      {:else}
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">$*>8#M/> ({inspections.length})</h5>
          </div>
          <div class="card-body">
            {#if inspections.length === 0}
              <div class="text-center py-5">
                <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">K#$M/>9@ $*>8#M/> "32M/> (>9@$</h5>
                <p class="text-muted">(5@( $*>8#@ 8A0B 0#M/>8> @ 50M/> ,#>50 M2? 0>.</p>
              </div>
            {:else}
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>8></th>
                      <th>M0>. .98B2 '?>0@</th>
                      <th>0AB &?(></th>
                      <th>$*>8#@ &?(></th>
                      <th>8M%?$@</th>
                      <th>C$@</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each inspections as inspection}
                      <tr>
                        <td>
                          <code class="small">{inspection.ID}</code>
                        </td>
                        <td>{inspection.8> || '-'}</td>
                        <td>{inspection.(>5 || '-'}</td>
                        <td>{inspection['0AB 9K#M/>> &?(>'] || '-'}</td>
                        <td>{inspection.$>0@ || '-'}</td>
                        <td>
                          <span class="badge bg-{inspection['B# M0G!'] === 'Pending' ? 'warning' : 'success'}">
                            {inspection['B# M0G!'] || 'Pending'}
                          </span>
                        </td>
                        <td>
                          <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" title="View Details">
                              <i class="fas fa-eye"></i>
                            </button>
                            {#if inspection['+>2 2?']}
                              <a href={inspection['+>2 2?']} target="_blank" class="btn btn-outline-info" title="View File">
                                <i class="fas fa-file"></i>
                              </a>
                            {/if}
                            <button class="btn btn-outline-secondary" title="Export PDF">
                              <i class="fas fa-file-pdf"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .table th {
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .badge {
    font-size: 0.75rem;
  }

  .btn-group-sm .btn {
    padding: 0.25rem 0.5rem;
  }
</style>
