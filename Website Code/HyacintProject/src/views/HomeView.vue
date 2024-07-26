<template>
  <main>
    <h1>Water Hyacinth location BY Centre for Biological Control</h1>
    <img src="../../public/images/logoCBC.jpg" alt="CBC logo"/>
    <article id="buttons">
      <button @click="navigateToPredictionView(-25.7500, 27.8533, -25.720774, 27.784343, 25.780000, 27.907111)">
        Hartbeespoort Dam
      </button>
      <button @click="navigateToPredictionView(-25.3247, 27.46, -25.35, 27.50, 25.8, 27.91)">
        Other Dam
      </button>
    </article>
  </main>
</template>

<script lang="ts">
import router from "@/router";
import {defineComponent} from "vue";

export default defineComponent({
  setup() {
    const navigateToPredictionView = (latitude: number, longitude: number, X: number, Y: number, pictureX: number, pictureY: number) => {
      router.push({
        name: 'predictionView',
        query: {
          latitude: latitude,
          longitude: longitude,
          X1: X,
          Y1: Y,
          X2: pictureX,
          Y2: pictureY
        }
      });
    };
    return {
      navigateToPredictionView,
    };
  }
});

</script>

<style scoped>
h1 {
  text-align: center;
  margin: 50px auto 20px auto;
}

img {
  display: block;
  margin: 50px auto;
}

#buttons {
  text-align: center;
}

button {
  padding: 10px 30px;
  margin-left: 20px;
  background-color: #707330;
}

button > * {
  text-decoration: none;
  color: white;
}
</style>
