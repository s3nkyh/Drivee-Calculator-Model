--
-- PostgreSQL database dump
--

\restrict VvxKR6WshWgmohKAJg1yc4RjcazoVFnmm1EUGPN8MuFWOHZfa66LRUAembpPrLL

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: borrowing_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.borrowing_status AS ENUM (
    'BORROWED',
    'RETURNED',
    'OVERDUE'
);


ALTER TYPE public.borrowing_status OWNER TO postgres;

--
-- Name: update_available_copies(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_available_copies() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE books
        SET available_copies = available_copies - 1
        WHERE id = NEW.book_id;

    ELSIF TG_OP = 'UPDATE' AND NEW.return_date IS NOT NULL AND OLD.return_date IS NULL THEN
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE id = NEW.book_id;
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_available_copies() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    author_id integer NOT NULL,
    genre_id integer,
    published_year integer,
    available_copies integer DEFAULT 1,
    total_copies integer DEFAULT 1,
    CONSTRAINT books_available_copies_check CHECK ((available_copies >= 0)),
    CONSTRAINT books_published_year_check CHECK ((published_year > 0)),
    CONSTRAINT books_total_copies_check CHECK ((total_copies >= 1))
);


ALTER TABLE public.books OWNER TO postgres;

--
-- Name: borrowings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.borrowings (
    id integer NOT NULL,
    book_id integer NOT NULL,
    reader_id integer NOT NULL,
    borrowed_date date DEFAULT CURRENT_DATE NOT NULL,
    due_date date NOT NULL,
    returned_date date,
    status public.borrowing_status DEFAULT 'BORROWED'::public.borrowing_status NOT NULL
);


ALTER TABLE public.borrowings OWNER TO postgres;

--
-- Name: readers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.readers (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    phone character varying(20),
    membership_date date DEFAULT CURRENT_DATE,
    is_active boolean DEFAULT true
);


ALTER TABLE public.readers OWNER TO postgres;

--
-- Name: active_borrowings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_borrowings AS
 SELECT b.id AS borrowing_id,
    r.name AS reader_name,
    bk.title AS book_title,
    b.borrowed_date,
    (CURRENT_DATE - b.borrowed_date) AS days_borrowed
   FROM ((public.borrowings b
     JOIN public.readers r ON ((b.reader_id = r.id)))
     JOIN public.books bk ON ((b.book_id = bk.id)))
  WHERE (b.returned_date IS NULL);


ALTER VIEW public.active_borrowings OWNER TO postgres;

--
-- Name: authors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.authors (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    birth_date date,
    country character varying(50)
);


ALTER TABLE public.authors OWNER TO postgres;

--
-- Name: authors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.authors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.authors_id_seq OWNER TO postgres;

--
-- Name: authors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.authors_id_seq OWNED BY public.authors.id;


--
-- Name: books_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.books_id_seq OWNER TO postgres;

--
-- Name: books_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.books_id_seq OWNED BY public.books.id;


--
-- Name: borrowings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.borrowings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.borrowings_id_seq OWNER TO postgres;

--
-- Name: borrowings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.borrowings_id_seq OWNED BY public.borrowings.id;


--
-- Name: genres; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.genres (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.genres OWNER TO postgres;

--
-- Name: genres_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.genres_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.genres_id_seq OWNER TO postgres;

--
-- Name: genres_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.genres_id_seq OWNED BY public.genres.id;


--
-- Name: readers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.readers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.readers_id_seq OWNER TO postgres;

--
-- Name: readers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.readers_id_seq OWNED BY public.readers.id;


--
-- Name: authors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors ALTER COLUMN id SET DEFAULT nextval('public.authors_id_seq'::regclass);


--
-- Name: books id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books ALTER COLUMN id SET DEFAULT nextval('public.books_id_seq'::regclass);


--
-- Name: borrowings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrowings ALTER COLUMN id SET DEFAULT nextval('public.borrowings_id_seq'::regclass);


--
-- Name: genres id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres ALTER COLUMN id SET DEFAULT nextval('public.genres_id_seq'::regclass);


--
-- Name: readers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.readers ALTER COLUMN id SET DEFAULT nextval('public.readers_id_seq'::regclass);


--
-- Name: authors authors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_pkey PRIMARY KEY (id);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);


--
-- Name: borrowings borrowings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrowings
    ADD CONSTRAINT borrowings_pkey PRIMARY KEY (id);


--
-- Name: genres genres_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_name_key UNIQUE (name);


--
-- Name: genres genres_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.genres
    ADD CONSTRAINT genres_pkey PRIMARY KEY (id);


--
-- Name: readers readers_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.readers
    ADD CONSTRAINT readers_email_key UNIQUE (email);


--
-- Name: readers readers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.readers
    ADD CONSTRAINT readers_pkey PRIMARY KEY (id);


--
-- Name: idx_books_author; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_books_author ON public.books USING btree (author_id);


--
-- Name: idx_books_genre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_books_genre ON public.books USING btree (genre_id);


--
-- Name: idx_borrowings_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_borrowings_status ON public.borrowings USING btree (status);


--
-- Name: idx_readers_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_readers_email ON public.readers USING btree (email);


--
-- Name: borrowings trg_update_available_copies; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_available_copies AFTER INSERT OR UPDATE ON public.borrowings FOR EACH ROW EXECUTE FUNCTION public.update_available_copies();


--
-- Name: books books_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.authors(id) ON DELETE CASCADE;


--
-- Name: books books_genre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_genre_id_fkey FOREIGN KEY (genre_id) REFERENCES public.genres(id) ON DELETE SET NULL;


--
-- Name: borrowings borrowings_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrowings
    ADD CONSTRAINT borrowings_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id) ON DELETE CASCADE;


--
-- Name: borrowings borrowings_reader_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.borrowings
    ADD CONSTRAINT borrowings_reader_id_fkey FOREIGN KEY (reader_id) REFERENCES public.readers(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict VvxKR6WshWgmohKAJg1yc4RjcazoVFnmm1EUGPN8MuFWOHZfa66LRUAembpPrLL

