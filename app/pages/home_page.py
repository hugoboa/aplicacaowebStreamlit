import streamlit as st

def home_page():
    # Verificar se o usuário está logado
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()  # Interrompe a execução para evitar a exibição da página

    # CSS para o carrossel
    st.markdown(
        """
        <style>
        body {
            background-color: #f7f9fc;
        }
        .carousel-container {
            max-width: 800px;
            margin: 0 auto;
            overflow: hidden;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .carousel {
            display: flex;
            transition: transform 0.5s ease-in-out;
        }
        .carousel img {
            width: 100%;
            flex-shrink: 0;
            border-radius: 10px;
        }
        .buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }
        .buttons button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .buttons button:hover {
            background-color: #0056b3;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # HTML para o carrossel
    st.markdown(
        """
        <div class="carousel-container">
            <div class="carousel" id="carousel">
                <img src="https://onibusetransporte.com/wp-content/uploads/2024/11/Eucatur-6013-fr-ld-dir-scaled.jpg" alt="Imagem 1">
                <img src="https://i0.wp.com/madeiraoweb.com.br/wp-content/uploads/2024/03/onibus-eucatur-60-anos-scaled.jpg?resize=768%2C512&ssl=1" alt="Imagem 2">
                <img src="https://via.placeholder.com/800x300?text=Imagem+3" alt="Imagem 3">
            </div>
        </div>
        <div class="buttons">
            <button onclick="prev()">Anterior</button>
            <button onclick="next()">Próximo</button>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # JavaScript para alternar entre imagens
    st.markdown(
        """
        <script>
        let currentIndex = 0;
        const images = document.querySelectorAll('.carousel img');
        const totalImages = images.length;

        function updateCarousel() {
            const carousel = document.getElementById('carousel');
            carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
        }

        function next() {
            currentIndex = (currentIndex + 1) % totalImages;
            updateCarousel();
        }

        function prev() {
            currentIndex = (currentIndex - 1 + totalImages) % totalImages;
            updateCarousel();
        }
        </script>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    home_page()
