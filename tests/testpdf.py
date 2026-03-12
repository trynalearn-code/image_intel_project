if __name__ == "__main__":
    pdf_data = generate_pdf("Hello PDF")

    with open("test.pdf", "wb") as f:
        f.write(pdf_data)

    print("PDF generated successfully")