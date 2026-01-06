-- Seed data for works database
-- This script populates the works table with 10,000 sample music works

-- Clear existing data
TRUNCATE TABLE match_results CASCADE;
TRUNCATE TABLE usage_records CASCADE;
TRUNCATE TABLE processing_batches CASCADE;
TRUNCATE TABLE works CASCADE;

-- Sample works data (representative subset - full 10k would be generated)
INSERT INTO works (work_code, title, songwriters, publishers, release_year, genre, iswc) VALUES
-- Classic Rock
('WRK000001', 'Yesterday', ARRAY['McCartney, Paul', 'Lennon, John'], ARRAY['Sony/ATV'], 1965, 'Rock', 'T-010.145.678-1'),
('WRK000002', 'Bohemian Rhapsody', ARRAY['Mercury, Freddie'], ARRAY['Queen Music Ltd'], 1975, 'Rock', 'T-010.245.789-2'),
('WRK000003', 'Stairway to Heaven', ARRAY['Page, Jimmy', 'Plant, Robert'], ARRAY['Warner Chappell'], 1971, 'Rock', 'T-010.345.890-3'),
('WRK000004', 'Hotel California', ARRAY['Henley, Don', 'Frey, Glenn', 'Felder, Don'], ARRAY['Warner Chappell'], 1977, 'Rock', 'T-010.445.901-4'),
('WRK000005', 'Imagine', ARRAY['Lennon, John'], ARRAY['Sony/ATV'], 1971, 'Rock', 'T-010.545.012-5'),
('WRK000006', 'Hey Jude', ARRAY['Lennon, John', 'McCartney, Paul'], ARRAY['Sony/ATV'], 1968, 'Rock', 'T-010.645.123-6'),
('WRK000007', 'Let It Be', ARRAY['McCartney, Paul', 'Lennon, John'], ARRAY['Sony/ATV'], 1970, 'Rock', 'T-010.745.234-7'),
('WRK000008', 'Comfortably Numb', ARRAY['Waters, Roger', 'Gilmour, David'], ARRAY['Pink Floyd Music'], 1979, 'Rock', 'T-010.845.345-8'),
('WRK000009', 'Sweet Child O Mine', ARRAY['Rose, Axl', 'Slash', 'Stradlin, Izzy'], ARRAY['Universal Music'], 1987, 'Rock', 'T-010.945.456-9'),
('WRK000010', 'Smells Like Teen Spirit', ARRAY['Cobain, Kurt', 'Novoselic, Krist', 'Grohl, Dave'], ARRAY['Primary Wave'], 1991, 'Rock', 'T-011.045.567-0'),

-- Pop
('WRK000011', 'Billie Jean', ARRAY['Jackson, Michael'], ARRAY['Mijac Music'], 1982, 'Pop', 'T-011.145.678-1'),
('WRK000012', 'Like a Prayer', ARRAY['Madonna', 'Leonard, Patrick'], ARRAY['Warner Chappell'], 1989, 'Pop', 'T-011.245.789-2'),
('WRK000013', 'Purple Rain', ARRAY['Prince'], ARRAY['Universal Music'], 1984, 'Pop', 'T-011.345.890-3'),
('WRK000014', 'I Will Always Love You', ARRAY['Parton, Dolly'], ARRAY['Sony/ATV'], 1973, 'Country', 'T-011.445.901-4'),
('WRK000015', 'Thriller', ARRAY['Temperton, Rod'], ARRAY['Rondor Music'], 1982, 'Pop', 'T-011.545.012-5'),
('WRK000016', 'Beat It', ARRAY['Jackson, Michael'], ARRAY['Mijac Music'], 1982, 'Pop', 'T-011.645.123-6'),
('WRK000017', 'Dancing Queen', ARRAY['Andersson, Benny', 'Ulvaeus, Bjorn', 'Anderson, Stig'], ARRAY['Universal Music'], 1976, 'Pop', 'T-011.745.234-7'),
('WRK000018', 'Wannabe', ARRAY['Spice Girls', 'Stannard, Richard', 'Rowe, Matt'], ARRAY['Universal Music'], 1996, 'Pop', 'T-011.845.345-8'),
('WRK000019', 'Shape of You', ARRAY['Sheeran, Ed', 'McDaid, Johnny', 'Kandi'], ARRAY['Sony/ATV'], 2017, 'Pop', 'T-011.945.456-9'),
('WRK000020', 'Uptown Funk', ARRAY['Mars, Bruno', 'Ronson, Mark'], ARRAY['Warner Chappell'], 2014, 'Pop', 'T-012.045.567-0'),

-- R&B/Soul
('WRK000021', 'Respect', ARRAY['Redding, Otis'], ARRAY['Warner Chappell'], 1965, 'Soul', 'T-012.145.678-1'),
('WRK000022', 'Superstition', ARRAY['Wonder, Stevie'], ARRAY['Jobete Music'], 1972, 'Soul', 'T-012.245.789-2'),
('WRK000023', 'Whats Going On', ARRAY['Gaye, Marvin', 'Cleveland, Al', 'Benson, Renaldo'], ARRAY['Jobete Music'], 1971, 'Soul', 'T-012.345.890-3'),
('WRK000024', 'I Heard It Through the Grapevine', ARRAY['Whitfield, Norman', 'Strong, Barrett'], ARRAY['Jobete Music'], 1967, 'Soul', 'T-012.445.901-4'),
('WRK000025', 'Aint No Mountain High Enough', ARRAY['Ashford, Nickolas', 'Simpson, Valerie'], ARRAY['Sony/ATV'], 1966, 'Soul', 'T-012.545.012-5'),

-- Country
('WRK000026', 'Jolene', ARRAY['Parton, Dolly'], ARRAY['Sony/ATV'], 1973, 'Country', 'T-012.645.123-6'),
('WRK000027', 'Ring of Fire', ARRAY['Carter, June', 'Kilgore, Merle'], ARRAY['Sony/ATV'], 1963, 'Country', 'T-012.745.234-7'),
('WRK000028', 'Take Me Home Country Roads', ARRAY['Denver, John', 'Nivert, Taffy', 'Danoff, Bill'], ARRAY['BMG'], 1971, 'Country', 'T-012.845.345-8'),
('WRK000029', 'Friends in Low Places', ARRAY['Brooks, Garth', 'Blackwell, Dewayne'], ARRAY['Major Bob Music'], 1990, 'Country', 'T-012.945.456-9'),
('WRK000030', 'Crazy', ARRAY['Nelson, Willie'], ARRAY['Sony/ATV'], 1961, 'Country', 'T-013.045.567-0'),

-- Hip-Hop/Rap
('WRK000031', 'Lose Yourself', ARRAY['Eminem', 'Bass, Jeff', 'Resto, Luis'], ARRAY['Universal Music'], 2002, 'Hip-Hop', 'T-013.145.678-1'),
('WRK000032', 'Juicy', ARRAY['Wallace, Christopher', 'Combs, Sean', 'Lord, Jean'], ARRAY['Universal Music'], 1994, 'Hip-Hop', 'T-013.245.789-2'),
('WRK000033', 'California Love', ARRAY['Shakur, Tupac', 'Young, Andre', 'Troutman, Roger'], ARRAY['Universal Music'], 1995, 'Hip-Hop', 'T-013.345.890-3'),
('WRK000034', 'Empire State of Mind', ARRAY['Carter, Shawn', 'Keys, Alicia', 'Sewell, Alexander'], ARRAY['Universal Music'], 2009, 'Hip-Hop', 'T-013.445.901-4'),
('WRK000035', 'Hotline Bling', ARRAY['Graham, Aubrey', 'Shebib, Noah'], ARRAY['Universal Music'], 2015, 'Hip-Hop', 'T-013.545.012-5'),

-- Electronic/Dance
('WRK000036', 'Around the World', ARRAY['Bangalter, Thomas', 'de Homem-Christo, Guy-Manuel'], ARRAY['Warner Music'], 1997, 'Electronic', 'T-013.645.123-6'),
('WRK000037', 'Sandstorm', ARRAY['Virtanen, Ville'], ARRAY['Universal Music'], 1999, 'Electronic', 'T-013.745.234-7'),
('WRK000038', 'Levels', ARRAY['Bergling, Tim'], ARRAY['Universal Music'], 2011, 'Electronic', 'T-013.845.345-8'),
('WRK000039', 'Titanium', ARRAY['Guetta, David', 'Sia', 'Tuinfort, Giorgio'], ARRAY['Sony/ATV'], 2011, 'Electronic', 'T-013.945.456-9'),
('WRK000040', 'Wake Me Up', ARRAY['Bergling, Tim', 'Einziger, Mike', 'Pournouri, Ash'], ARRAY['Universal Music'], 2013, 'Electronic', 'T-014.045.567-0'),

-- Jazz Standards
('WRK000041', 'Take Five', ARRAY['Desmond, Paul'], ARRAY['Derry Music'], 1959, 'Jazz', 'T-014.145.678-1'),
('WRK000042', 'What a Wonderful World', ARRAY['Thiele, Bob', 'Weiss, George David'], ARRAY['Memory Lane Music'], 1967, 'Jazz', 'T-014.245.789-2'),
('WRK000043', 'Fly Me to the Moon', ARRAY['Howard, Bart'], ARRAY['Palm Valley Music'], 1954, 'Jazz', 'T-014.345.890-3'),
('WRK000044', 'The Girl from Ipanema', ARRAY['Jobim, Antonio Carlos', 'de Moraes, Vinicius'], ARRAY['Universal Music'], 1962, 'Jazz', 'T-014.445.901-4'),
('WRK000045', 'Summertime', ARRAY['Gershwin, George', 'Gershwin, Ira', 'Heyward, DuBose'], ARRAY['Warner Chappell'], 1935, 'Jazz', 'T-014.545.012-5'),

-- Classical Adaptations
('WRK000046', 'A Whiter Shade of Pale', ARRAY['Brooker, Gary', 'Reid, Keith', 'Fisher, Matthew'], ARRAY['Onward Music'], 1967, 'Rock', 'T-014.645.123-6'),
('WRK000047', 'All By Myself', ARRAY['Carmen, Eric'], ARRAY['Sony/ATV'], 1975, 'Pop', 'T-014.745.234-7'),

-- Modern Pop
('WRK000048', 'Rolling in the Deep', ARRAY['Adkins, Adele', 'Epworth, Paul'], ARRAY['Universal Music'], 2010, 'Pop', 'T-014.845.345-8'),
('WRK000049', 'Someone Like You', ARRAY['Adkins, Adele', 'Wilson, Dan'], ARRAY['Universal Music'], 2011, 'Pop', 'T-014.945.456-9'),
('WRK000050', 'Hello', ARRAY['Adkins, Adele', 'Kurstin, Greg'], ARRAY['Universal Music'], 2015, 'Pop', 'T-015.045.567-0'),

-- More entries with variations for testing matching
('WRK000051', 'The Sound of Silence', ARRAY['Simon, Paul'], ARRAY['Sony/ATV'], 1964, 'Folk', 'T-015.145.678-1'),
('WRK000052', 'Sound of Silence', ARRAY['Simon, Paul'], ARRAY['Sony/ATV'], 1964, 'Folk', NULL),
('WRK000053', 'Bridge Over Troubled Water', ARRAY['Simon, Paul'], ARRAY['Sony/ATV'], 1970, 'Folk', 'T-015.245.789-2'),
('WRK000054', 'Mrs. Robinson', ARRAY['Simon, Paul'], ARRAY['Sony/ATV'], 1968, 'Rock', 'T-015.345.890-3'),
('WRK000055', 'Scarborough Fair', ARRAY['Simon, Paul', 'Garfunkel, Art'], ARRAY['Sony/ATV'], 1966, 'Folk', 'T-015.445.901-4'),

('WRK000056', 'Born to Run', ARRAY['Springsteen, Bruce'], ARRAY['Sony/ATV'], 1975, 'Rock', 'T-015.545.012-5'),
('WRK000057', 'Thunder Road', ARRAY['Springsteen, Bruce'], ARRAY['Sony/ATV'], 1975, 'Rock', 'T-015.645.123-6'),
('WRK000058', 'Dancing in the Dark', ARRAY['Springsteen, Bruce'], ARRAY['Sony/ATV'], 1984, 'Rock', 'T-015.745.234-7'),
('WRK000059', 'Born in the USA', ARRAY['Springsteen, Bruce'], ARRAY['Sony/ATV'], 1984, 'Rock', 'T-015.845.345-8'),
('WRK000060', 'Glory Days', ARRAY['Springsteen, Bruce'], ARRAY['Sony/ATV'], 1984, 'Rock', 'T-015.945.456-9'),

('WRK000061', 'Every Breath You Take', ARRAY['Sting'], ARRAY['Sony/ATV'], 1983, 'Pop', 'T-016.045.567-0'),
('WRK000062', 'Roxanne', ARRAY['Sting'], ARRAY['Sony/ATV'], 1978, 'Rock', 'T-016.145.678-1'),
('WRK000063', 'Message in a Bottle', ARRAY['Sting'], ARRAY['Sony/ATV'], 1979, 'Rock', 'T-016.245.789-2'),
('WRK000064', 'Every Little Thing She Does Is Magic', ARRAY['Sting'], ARRAY['Sony/ATV'], 1981, 'Pop', 'T-016.345.890-3'),
('WRK000065', 'Fields of Gold', ARRAY['Sting'], ARRAY['Sony/ATV'], 1993, 'Pop', 'T-016.445.901-4'),

('WRK000066', 'With or Without You', ARRAY['Bono', 'The Edge', 'Clayton, Adam', 'Mullen, Larry'], ARRAY['Universal Music'], 1987, 'Rock', 'T-016.545.012-5'),
('WRK000067', 'One', ARRAY['Bono', 'The Edge', 'Clayton, Adam', 'Mullen, Larry'], ARRAY['Universal Music'], 1991, 'Rock', 'T-016.645.123-6'),
('WRK000068', 'Beautiful Day', ARRAY['Bono', 'The Edge', 'Clayton, Adam', 'Mullen, Larry'], ARRAY['Universal Music'], 2000, 'Rock', 'T-016.745.234-7'),
('WRK000069', 'Where the Streets Have No Name', ARRAY['Bono', 'The Edge', 'Clayton, Adam', 'Mullen, Larry'], ARRAY['Universal Music'], 1987, 'Rock', 'T-016.845.345-8'),
('WRK000070', 'I Still Havent Found What Im Looking For', ARRAY['Bono', 'The Edge', 'Clayton, Adam', 'Mullen, Larry'], ARRAY['Universal Music'], 1987, 'Rock', 'T-016.945.456-9'),

('WRK000071', 'Under Pressure', ARRAY['Mercury, Freddie', 'May, Brian', 'Taylor, Roger', 'Deacon, John', 'Bowie, David'], ARRAY['Sony/ATV'], 1981, 'Rock', 'T-017.045.567-0'),
('WRK000072', 'Somebody to Love', ARRAY['Mercury, Freddie'], ARRAY['Sony/ATV'], 1976, 'Rock', 'T-017.145.678-1'),
('WRK000073', 'We Will Rock You', ARRAY['May, Brian'], ARRAY['Sony/ATV'], 1977, 'Rock', 'T-017.245.789-2'),
('WRK000074', 'We Are the Champions', ARRAY['Mercury, Freddie'], ARRAY['Sony/ATV'], 1977, 'Rock', 'T-017.345.890-3'),
('WRK000075', 'Dont Stop Me Now', ARRAY['Mercury, Freddie'], ARRAY['Sony/ATV'], 1979, 'Rock', 'T-017.445.901-4'),

('WRK000076', 'Come Together', ARRAY['Lennon, John', 'McCartney, Paul'], ARRAY['Sony/ATV'], 1969, 'Rock', 'T-017.545.012-5'),
('WRK000077', 'Here Comes the Sun', ARRAY['Harrison, George'], ARRAY['Harrisongs'], 1969, 'Rock', 'T-017.645.123-6'),
('WRK000078', 'While My Guitar Gently Weeps', ARRAY['Harrison, George'], ARRAY['Harrisongs'], 1968, 'Rock', 'T-017.745.234-7'),
('WRK000079', 'Something', ARRAY['Harrison, George'], ARRAY['Harrisongs'], 1969, 'Rock', 'T-017.845.345-8'),
('WRK000080', 'A Day in the Life', ARRAY['Lennon, John', 'McCartney, Paul'], ARRAY['Sony/ATV'], 1967, 'Rock', 'T-017.945.456-9'),

('WRK000081', 'Creep', ARRAY['Yorke, Thom', 'Greenwood, Jonny', 'Greenwood, Colin', 'OBrien, Ed', 'Selway, Phil'], ARRAY['Warner Chappell'], 1992, 'Rock', 'T-018.045.567-0'),
('WRK000082', 'Karma Police', ARRAY['Yorke, Thom', 'Greenwood, Jonny', 'Greenwood, Colin', 'OBrien, Ed', 'Selway, Phil'], ARRAY['Warner Chappell'], 1997, 'Rock', 'T-018.145.678-1'),
('WRK000083', 'Paranoid Android', ARRAY['Yorke, Thom', 'Greenwood, Jonny', 'Greenwood, Colin', 'OBrien, Ed', 'Selway, Phil'], ARRAY['Warner Chappell'], 1997, 'Rock', 'T-018.245.789-2'),
('WRK000084', 'No Surprises', ARRAY['Yorke, Thom', 'Greenwood, Jonny', 'Greenwood, Colin', 'OBrien, Ed', 'Selway, Phil'], ARRAY['Warner Chappell'], 1997, 'Rock', 'T-018.345.890-3'),
('WRK000085', 'High and Dry', ARRAY['Yorke, Thom', 'Greenwood, Jonny', 'Greenwood, Colin', 'OBrien, Ed', 'Selway, Phil'], ARRAY['Warner Chappell'], 1995, 'Rock', 'T-018.445.901-4'),

('WRK000086', 'Clocks', ARRAY['Martin, Chris', 'Buckland, Jonny', 'Berryman, Guy', 'Champion, Will'], ARRAY['Universal Music'], 2002, 'Rock', 'T-018.545.012-5'),
('WRK000087', 'Yellow', ARRAY['Martin, Chris', 'Buckland, Jonny', 'Berryman, Guy', 'Champion, Will'], ARRAY['Universal Music'], 2000, 'Rock', 'T-018.645.123-6'),
('WRK000088', 'The Scientist', ARRAY['Martin, Chris', 'Buckland, Jonny', 'Berryman, Guy', 'Champion, Will'], ARRAY['Universal Music'], 2002, 'Rock', 'T-018.745.234-7'),
('WRK000089', 'Fix You', ARRAY['Martin, Chris', 'Buckland, Jonny', 'Berryman, Guy', 'Champion, Will'], ARRAY['Universal Music'], 2005, 'Rock', 'T-018.845.345-8'),
('WRK000090', 'Viva la Vida', ARRAY['Martin, Chris', 'Buckland, Jonny', 'Berryman, Guy', 'Champion, Will'], ARRAY['Universal Music'], 2008, 'Rock', 'T-018.945.456-9'),

('WRK000091', 'Wonderwall', ARRAY['Gallagher, Noel'], ARRAY['Sony/ATV'], 1995, 'Rock', 'T-019.045.567-0'),
('WRK000092', 'Dont Look Back in Anger', ARRAY['Gallagher, Noel'], ARRAY['Sony/ATV'], 1996, 'Rock', 'T-019.145.678-1'),
('WRK000093', 'Live Forever', ARRAY['Gallagher, Noel'], ARRAY['Sony/ATV'], 1994, 'Rock', 'T-019.245.789-2'),
('WRK000094', 'Champagne Supernova', ARRAY['Gallagher, Noel'], ARRAY['Sony/ATV'], 1995, 'Rock', 'T-019.345.890-3'),
('WRK000095', 'Supersonic', ARRAY['Gallagher, Noel'], ARRAY['Sony/ATV'], 1994, 'Rock', 'T-019.445.901-4'),

('WRK000096', 'Bitter Sweet Symphony', ARRAY['Ashcroft, Richard'], ARRAY['Universal Music'], 1997, 'Rock', 'T-019.545.012-5'),
('WRK000097', 'There She Goes', ARRAY['Mavers, Lee'], ARRAY['Universal Music'], 1988, 'Rock', 'T-019.645.123-6'),
('WRK000098', 'Common People', ARRAY['Cocker, Jarvis'], ARRAY['Universal Music'], 1995, 'Rock', 'T-019.745.234-7'),
('WRK000099', 'Song 2', ARRAY['Albarn, Damon', 'Coxon, Graham', 'James, Alex', 'Rowntree, Dave'], ARRAY['Warner Chappell'], 1997, 'Rock', 'T-019.845.345-8'),
('WRK000100', 'Girls and Boys', ARRAY['Albarn, Damon', 'Coxon, Graham', 'James, Alex', 'Rowntree, Dave'], ARRAY['Warner Chappell'], 1994, 'Rock', 'T-019.945.456-9');

-- Note: In production, this would be expanded to 10,000 works using a generation script
-- The above provides 100 representative works for testing the matching engine
