<script lang="ts">
  import { socket } from "../lib/socket";
  import { n_packets, packets_sent } from "../lib/sender";
</script>

<div
  style="margin: 0.5em; padding: 0.5em; border: 3px solid green; background: lightgreen; border-radius: 10px;"
>
  {#if $n_packets > 0}
    {#if $packets_sent < $n_packets}
      Whatsapp Sender: {$packets_sent} / {$n_packets}
    {:else}
      Whatsapp Sender: Finito!
    {/if}
  {:else}
    Whatsapp Sender: in attesa
  {/if}
</div>
